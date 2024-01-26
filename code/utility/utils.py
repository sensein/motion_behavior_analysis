import os
import mimetypes
import shutil
import argparse
import json

def is_video_file(file_path):
    """
    Check if the given file is a video file.

    :param file_path: str, the path to the file
    :return: bool, True if the file is a video file, False otherwise
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type is not None and mime_type.startswith('video/')

def find_video_files(list_of_folders):
    """
    Find video files in the given list of folders and return a list of paths to the video files.
    
    :param list_of_folders: A list of folder paths to search for video files.
    :type list_of_folders: list
    :return: A list of paths to the found video files.
    :rtype: list
    """
    video_files = []
    for folder in list_of_folders:
        for root, dirs, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                if is_video_file(file_path):
                    video_files.append(file_path)
    return video_files

def find_folders_with_multiple_videos(workspace):
    """
    Find folders with multiple video files in the given workspace.

    Args:
        workspace (str): The path of the workspace to search for folders with multiple video files.

    Returns:
        list: A list of paths of the folders with more than one video file.
    """
    folders_with_multiple_videos = [] # This will hold the paths of the folders with more than one video file

    # Walk through all subfolders in the given folder
    for root, dirs, files in os.walk(workspace):
        video_files = []
        for file in files:
            if is_video_file(os.path.join(root, file)):
                video_files.append(os.path.join(root, file))

        # If there are more than one video files, add the folder to the list
        if len(video_files) > 1:
            folders_with_multiple_videos.append(root)

    return folders_with_multiple_videos

def remove_directory(dir_path):
    """
    Removes the specified directory and all its contents if it exists.

    Parameters:
    dir_path (str): The path of the directory to be removed.

    Returns:
    None
    """
    # Check if the directory exists
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        # Remove the directory and all its contents
        shutil.rmtree(dir_path)
        print(f"Directory '{dir_path}' has been removed successfully.")
    return

def read_config(workspace):
    """
    Read a configuration file and return its contents as a dictionary.

    Args:
        workspace (str): The directory where the configuration file is located.

    Returns:
        dict: The contents of the configuration file as a dictionary.
    """
    config_path = os.path.join(workspace, 'config.json')
    with open(config_path, 'r') as file:
        return json.load(file)

def get_workspace():
    """
    Get the workspace directory path from the command line arguments.

    :return: The path to the workspace directory.
    """
    parser = argparse.ArgumentParser(description='Process and sync video files.')
    parser.add_argument('--workspace', help='The path to the workspace directory')
    args = parser.parse_args()
    return args.workspace
