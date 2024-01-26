import os
from .utils import *
from Pose2Sim.Utilities.Blazepose_runsave import blazepose_detec_func

def extract_pose_from_videos(workspace, settings):
    """
    Extracts pose from videos using the provided workspace and settings.

    Args:
        workspace: The workspace where the videos are located.
        settings: The settings for the pose extraction.

    Returns:
        None
    """
    task_folders = get_tasks_to_extract_pose([workspace])
    for task_folder in task_folders:
        my_human_pose_estimation(task_folder, settings)

def get_tasks_to_extract_pose(list_of_folders):
    """
    Get a list of folders and find video files within those folders. 
    Exclude files containing '__synced__', 'Calibration', or 'pose' in their paths. 
    Return a sorted list of unique folder paths containing the video files.
    """
    files = [
        file for file in find_video_files(list_of_folders) if
        '__synced__' in file and
        not (f'{os.sep}Calibration{os.sep}' in file or f'{os.sep}pose{os.sep}' in file or f'{os.sep}unset_unset_unset_unset{os.sep}' in file)
    ]

    folders = set()
    for path in files:
        # Split the path into folders
        parts = path.split('/')
        # Remove the last part (filename) and 'raw' if present
        folders_without_file = [part for part in parts[:-1] if part != 'raw']
        # Reconstruct the folder path
        folder_path = '/'.join(folders_without_file)
        folders.add(folder_path)

    # Converting the set to a sorted list
    sorted_folders = sorted(list(folders))
    return sorted_folders

def my_human_pose_estimation(task_folder, settings):
    """
    Performs human pose estimation based on the specified task folder and settings.

    Args:
        task_folder (str): The folder containing the task.
        settings (dict): The settings for the pose estimation.

    Raises:
        Exception: If the specified model has not been integrated.

    Returns:
        None
    """
    output_folder = os.path.join(task_folder, "pose")
    for file_name in os.listdir(os.path.join(task_folder, "raw")):
        file_path = os.path.join(task_folder, "raw", file_name)
        if is_video_file(file_path):
            if settings['pose_framework'] == 'mediapipe' and settings['pose_model'] == 'BLAZEPOSE':
                json_output_folder = os.path.join(output_folder, f"blaze_{os.path.splitext(file_name)[0]}_json")
                if not os.path.exists(json_output_folder):
                    args = {
                        'input_file': file_path,
                        'to_csv': settings['to_csv'], 'to_h5': settings['to_h5'], 'to_json': True,
                        'display': settings['display'], 'save_images': settings['save_images'],
                        'save_video': settings['save_video'],
                        'model_complexity': f'{settings["model_complexity"]}',  # can be 0 (fast), 1, 2 (slow)
                        'output_folder': output_folder}
                    blazepose_detec_func(**args)
            else:
                raise Exception(f"The specified model has not been integrated, yet.")