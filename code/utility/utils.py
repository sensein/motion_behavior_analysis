"""
Module description: This module contains a set of utility functions.
"""

import logging
import logging.handlers
import os
import mimetypes
import shutil
import argparse
import json
import sys

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
    for root, _, files in os.walk(workspace):
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
        logging.info(f"Directory '{dir_path}' has been removed successfully.")
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
    with open(config_path, 'r', encoding='utf-8') as file:
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
        if is_video_file(subfile) and "raw" in dirpath
    ]
    base_names.update(subfiles)
    return base_names

def move_logs_to_workspace(workspace, task):
    """
    Move the logs to the workspace directory.

    Parameters:
    workspace (str): The path to the workspace directory.
    task (str): The name of the task being processed.

    Returns:
    None
    """
    
    for root, _, files in os.walk(workspace):
        if 'logs.txt' in files:
            # Construct the full path to the found logs.txt file
            logs_path = os.path.join(root, 'logs.txt')
            
            # Define the new filename with the task-specific name
            new_logs_path = os.path.join(root, f'logs_{task}.txt')
            
            # Move and rename the logs.txt to logs_{task}.txt
            shutil.move(logs_path, new_logs_path)
            
            logging.info(f"logs.txt found and moved to {new_logs_path}")
            break  # Stop the search after finding and moving the first logs.txt file
    else:
        # This part executes if the for loop completes without finding logs.txt
        logging.error("logs.txt not found in the workspace.")

class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.

    Attributes:
        logger (Logger): The logger instance to redirect writes to.
        log_level (int): The log level to use for the redirected writes.
        linebuf (str): Buffer to store partial lines of text.

    Methods:
        write(buf): Writes the given buffer to the logger, splitting it into lines and logging each line separately.
        flush(): Does nothing.

    """ 
    """
    Initialize the class with a logger and a log level.
    
    Parameters:
        logger: The logger object to be used for logging.
        log_level: The log level for the logger, defaults to logging.INFO.
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    """
    Write the given buffer to the logger with the specified log level.
    
    Args:
        buf: A string containing the buffer to be written to the logger.
    
    Returns:
        None
    """
    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    """
    Does nothing.
    """
    def flush(self):
        pass

def setup_logging(workspace, task):
    """
    Set up logging for the workspace and task.

    Args:
        workspace (str): The workspace directory.
        task (str): The task name.

    Returns:
        None
    """
    # Define the filename for the log file
    log_filename = f"{workspace}/mylogs_{task}.txt"

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        filename=log_filename, 
                        filemode='a')

    stdout_logger = logging.getLogger('STDOUT')
    sl = StreamToLogger(stdout_logger, logging.INFO)
    sys.stdout = sl

    stderr_logger = logging.getLogger('STDERR')
    sl = StreamToLogger(stderr_logger, logging.ERROR)
    sys.stderr = sl