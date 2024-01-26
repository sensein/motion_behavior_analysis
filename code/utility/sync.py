import shutil
import os
import torch
from moviepy.editor import VideoFileClip
from .utils import *

def get_folders_to_be_synced(workspace):
    """
    Returns a list of folders to be synced based on the provided workspace.

    :param workspace: The workspace to search for folders.
    :type workspace: str
    :return: A list of folders to be synced.
    :rtype: list
    """
    folders_to_sync = [ folder for folder in find_folders_with_multiple_videos(workspace) if
                       f'{os.sep}original{os.sep}' in folder
    ]
    return folders_to_sync

def get_synced_folders(workspace):
    """
    Returns a list of subfolders in the given workspace that contain '__synced__' in their name.

    Args:
        workspace: A string representing the path of the workspace.

    Returns:
        A list of subfolders containing '__synced__' in their name.
    """
    return [os.path.join(root, folder) for root, dirs, files in os.walk(workspace) for folder in dirs if '__synced__' in folder]


def trim_video_before_audio_spike(video_path):
    """
    Trims a video before an audio spike.

    Args:
        video_path (str): The path to the video file.

    Returns:
        float: The duration of the trimmed video.
    """
    clip = VideoFileClip(video_path)
    audio = clip.audio

    if not audio:
        raise Exception(f"Video {video_path} doesn't have any audio.")

    fps = audio.fps
    audio_frames = audio.to_soundarray(fps=fps)
    energy = torch.tensor(audio_frames ** 2).sum(dim=1)
    threshold = torch.mean(energy) + 2 * torch.std(energy)
    spike_indices = torch.where(energy > threshold)[0]

    if len(spike_indices) == 0:
        print("No audio spike found exceeding the threshold. Skipping trimming.")
        return clip.duration

    spike_frame = spike_indices[0].item()
    spike_time = spike_frame / fps
    trimmed_clip = clip.subclip(spike_time)

    new_folder = os.path.split(video_path)[0].replace(f"{os.sep}original{os.sep}", f"{os.sep}__synced__{os.sep}")
    os.makedirs(new_folder, exist_ok=True)

    new_file_path = os.path.join(new_folder, os.path.split(video_path)[1])
    trimmed_clip.write_videofile(new_file_path, codec="libx264", audio=False)

    clip.close()
    trimmed_clip.close()

    return trimmed_clip.duration

def trim_video_after_a_while(file_path, new_duration):
    """
    Trims a video file to the specified duration and replaces the original file with the trimmed version.

    Args:
        file_path (str): The path to the video file to be trimmed.
        new_duration (float): The new duration in seconds to trim the video to.

    Returns:
        str: The file path of the trimmed video.
    """
    video = VideoFileClip(file_path).subclip(0, new_duration)
    format = os.path.splitext(file_path)[1]
    temp_file_path = file_path.replace(f'{format}', f'_temp{format}')
    video.write_videofile(temp_file_path, codec='libx264', audio=False)
    video.close()
    os.remove(file_path)
    os.rename(temp_file_path, file_path)
    return file_path

def copy_calibration_files(workspace):
    """
    Copy calibration files from the specified workspace to a new location.

    Args:
        workspace (str): The path of the workspace to copy the calibration files from.

    Returns:
        None
    """
    for root, dirs, files in os.walk(workspace):
        for file in files:
            file_path = os.path.join(root, file)
            if f"{os.sep}original{os.sep}" in file_path:
                new_file_path = file_path.replace(f"{os.sep}original{os.sep}", f"{os.sep}__synced__{os.sep}")
                if not os.path.exists(new_file_path):
                    os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
                    shutil.copy(file_path, new_file_path)

def sync_videos(workspace):
    """
    Synchronizes video files in the given workspace.

    Args:
        workspace: A string representing the path of the workspace.

    Returns:
        None
    """
    folders_to_be_synced = get_folders_to_be_synced(workspace)
    for folder_to_be_synced in folders_to_be_synced:
        files_to_be_synced = [
            file for file in find_video_files([folder_to_be_synced])
            if not (f'{os.sep}raw{os.sep}' in file and os.path.exists(
                file.replace(f'{os.sep}original{os.sep}', f'{os.sep}__synced__{os.sep}')))
        ]
        if not files_to_be_synced:
            continue
        durations = [trim_video_before_audio_spike(file) for file in files_to_be_synced]
        final_duration = min(durations)
        for file in files_to_be_synced:
            trimmed_file = file.replace(f'{os.sep}original{os.sep}', f'{os.sep}__synced__{os.sep}')
            trim_video_after_a_while(trimmed_file, final_duration)
    copy_calibration_files(workspace)