import os
from .utils import *
from moviepy.editor import VideoFileClip
import numpy as np
import cv2
import itertools

def get_first_frame_dimensions_and_orientation(video_path):
    """
    Get the dimensions and orientation of the first frame of a video.

    Args:
        video_path (str): The path to the video file.

    Returns:
        tuple: A tuple containing the height, width, and orientation of the frame.
    """
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Check if the video was opened successfully
    if not cap.isOpened():
        raise IOError(f"Cannot open video file {video_path}")

    # Read the first frame
    ret, frame = cap.read()

    # Close the video file
    cap.release()

    if not ret:
        raise IOError("Cannot read the first frame of the video")

    # Get dimensions of the frame
    height, width = frame.shape[:2]

    # Determine the orientation
    orientation = "portrait" if height > width else "landscape"

    # Return the dimensions and orientation of the frame
    return (height, width, orientation)


def get_videos_to_be_preprocessed(workspace, setting):
    """
    Get videos to be preprocessed based on the workspace and setting parameters.

    Args:
        workspace (str): The workspace directory.
        setting (dict): Dictionary containing fps, resolution, and format settings.

    Returns:
        list: List of files to be preprocessed.
    """
    if setting['fps'] is None and setting['resolution'][0] is None and setting['resolution'][1] is None and setting['format'] is None:
        return []

    my_fps = setting['fps'] if setting['fps'] is not None else 'unset'
    my_x = setting['resolution'][0] if setting['resolution'][0] is not None else 'unset'
    my_y = setting['resolution'][1] if setting['resolution'][1] is not None else 'unset'
    my_format = setting['format'] if setting['format'] is not None else 'unset'

    files_to_be_preprocessed = [
        file for file in find_video_files([workspace]) if
        (f'{os.sep}__synced__{os.sep}' in file and 
            f'{os.sep}all_cams{os.sep}' in file and 
            f'{os.sep}unset_unset_unset_unset{os.sep}' in file and 
            setting["format"] is not 'unset' and 
            not os.path.exists(file.replace('{os.sep}unset_unset_unset_unset{os.sep}', f'{os.sep}{my_fps}_{my_x}_{my_y}_{my_format}{os.sep}')[:-4] + f'.{my_format}')
        )
    ]
    return files_to_be_preprocessed

def create_new_file_path(file_path, fps, resolution, format):
    """
    Create a new file path based on the given file path, fps, resolution, and format.

    :param file_path: The original file path.
    :param fps: Frames per second of the new file path.
    :param resolution: The resolution of the new file path.
    :param format: The format of the new file path.
    :return: The new file path.
    """
    x, y = resolution

    # Ensure x and y are ordered alphabetically (vertical before horizontal)
    if x is not None and y is not None and y > x:
        x, y = y, x

    fps = 'unset' if fps is None else fps
    x = 'unset' if x is None else x
    y = 'unset' if y is None else y

    new_file_path = file_path.replace(f'{os.sep}unset_unset_unset_unset{os.sep}', f'{os.sep}{fps}_{x}_{y}_{format}{os.sep}')[:-4] + f'.{format}'
    return new_file_path

def compute_new_resolution(current_height, current_width, current_orientation, new_resolution):
    """
    Compute the new resolution based on the current resolution, orientation, and new resolution values.

    Args:
        current_height (int): The current height in pixels.
        current_width (int): The current width in pixels.
        current_orientation (str): The current orientation, either 'portrait' or 'landscape'.
        new_resolution (tuple): A tuple containing the new height and width in pixels.

    Returns:
        tuple: A tuple containing the new height and width in pixels.
    """
    # Unpack the new_resolution values
    new_height, new_width = new_resolution

    # Both values missing
    if new_height is None and new_width is None:
        return current_height, current_width

    # Maintain aspect ratio if one value is missing
    aspect_ratio = current_width / current_height
    if new_height is None:
        new_height = int(new_width / aspect_ratio)
    elif new_width is None:
        new_width = int(new_height * aspect_ratio)

    # Correct orientation if both values are provided
    if current_orientation == 'portrait' and new_width > new_height:
        new_height, new_width = new_width, new_height
    elif current_orientation == 'landscape' and new_height > new_width:
        new_height, new_width = new_width, new_height

    return new_height, new_width

def get_fps(video_file):
    """
    Get frames per second from a video file.

    Args:
        video_file (str): The file path to the video.

    Returns:
        float: Frames per second of the video.
    """
    video = VideoFileClip(video_file)
    fps = video.fps
    video.close()
    return fps

def preprocess_video(video_file, target_fps, target_resolution, format):
    """
    Preprocesses a video file to the specified target frames per second and resolution.

    Args:
        video_file (str): The path to the input video file.
        target_fps (int): The desired frames per second for the output video.
        target_resolution (tuple): The desired width and height for the output video.
        format (str): The format of the output video file.

    Returns:
        None
    """
    output_file = create_new_file_path(video_file, target_fps, target_resolution, format)
    
    if not os.path.exists(output_file):
        directory_name = os.path.dirname(output_file)
        os.makedirs(directory_name, exist_ok=True)

        current_height, current_width, current_orientation = get_first_frame_dimensions_and_orientation(video_file)
        current_fps = get_fps(video_file)
        new_height, new_width = compute_new_resolution(current_height, current_width, current_orientation, target_resolution)
        if not target_fps:
            new_fps = current_fps
        else:
            new_fps = target_fps

        if np.ceil(current_fps) < new_fps:
            print(f"Current fps ({current_fps}) in {video_file} is lower than the target fps ({new_fps}).")
            raise ValueError(os.path.dirname(output_file))

        current_aspect_ratio = current_width / current_height
        new_aspect_ratio = new_width / new_height
        if new_width > current_width or new_height > current_height:
            print(
                f"Current resolution ({[current_height, current_width]}) in {video_file} is smaller than the target resolution ({[new_height, new_width]}).")
            raise ValueError(os.path.dirname(output_file))

        video = VideoFileClip(video_file)
        new_video = video.set_fps(new_fps).resize([new_width, new_height])
        new_video.write_videofile(output_file, codec='libx264')
        new_video.close()
        video.close()
    return

def preprocess_videos(workspace, setting):
    """
    Preprocesses videos based on the provided workspace and settings.

    Args:
        workspace (str): The directory where the videos are located.
        setting (dict): A dictionary containing the preprocessing settings including
            'fps' (int): Frames per second
            'resolution' (str): Resolution of the video
            'format' (str): Video format

    Returns:
        None
    """
    fps = setting['fps']
    resolution = setting['resolution']
    format = setting['format']
    video_files = get_videos_to_be_preprocessed(workspace, setting)
    for video_file in video_files:
        try:
            preprocess_video(video_file, fps, resolution, format)
        except ValueError as e:
            # print(e)
            remove_directory(str(e))
            break

def find_unique_base_names(folder_path):
    """
    Returns a set of unique base names from the video files found in the specified folder path.

    Parameters:
    folder_path (str): The path to the folder containing the video files.

    Returns:
    set: A set of unique base names derived from the video file names.
    """
    base_names = set()
    subfiles = [
        os.path.splitext(subfile)[0] 
        for dirpath, dirnames, filenames in os.walk(folder_path) 
        for subfile in filenames 
        if is_video_file(subfile)
    ]
    base_names.update(subfiles)
    return base_names

def find_all_cams_folders(root_path):
    """
    Find all folders named "all_cams" containing "__synced__" in the given root path.
    
    :param root_path: The root path to search for "all_cams" folders.
    :return: A list of paths to the "all_cams" folders containing "__synced__".
    """
    all_cams_folders = []
    for root, dirs, files in os.walk(root_path):
        for dir in dirs:
            if dir == f"{os.sep}all_cams{os.sep}" and f"{os.sep}__synced__{os.sep}" and not f"{os.sep}pose{os.sep}" in os.path.join(root, dir):
                all_cams_folders.append(os.path.join(root, dir))
    return all_cams_folders

def create_sub_setups(workspace):
    """
    Create sub setups for the given workspace using the folders and files found in the workspace.
    """
    folders = find_all_cams_folders(workspace)
    for folder in folders:
        files = [os.path.join(root, file) for root, dirs, files in os.walk(folder) for file in files if is_video_file(file)]
        cameras = find_unique_base_names(folder)
        for i in range(len(cameras) - 1, 1, -1):
            combinations = list(itertools.combinations(cameras, i))
            for combo in combinations:
                subfolder_name = '_'.join(sorted(combo))
                for file in files:
                    if any(camera in file for camera in combo):
                        new_file = file.replace(f"{os.sep}all_cams{os.sep}", f"{os.sep}{subfolder_name}{os.sep}")
                        if not os.path.exists(new_file):
                            os.makedirs(os.path.dirname(new_file), exist_ok=True)
                            shutil.copy(file, new_file)