"""
Module description: This module contains the main functionality for syncing 
and pre-processing videos and extracting human pose.
"""

import logging
import logging.handlers
from utility.utils import get_workspace, read_config, move_logs_to_workspace, setup_logging
from utility.sync import sync_videos
from utility.preprocess import preprocess_videos, create_sub_setups
from utility.human_pose_estimation import extract_pose_from_videos

if __name__ == "__main__":
    # Read workspace
    workspace = get_workspace()

    # Read the configuration file
    config = read_config(workspace)

    # Setup logging
    setup_logging(workspace, 'preprocessing')

    # Sync the videos
    logging.info('Sync the videos...')
    sync_videos(workspace)

    # Preprocess videos based on the settings in the config file
    logging.info('Preprocessing videos based on the settings in the config file...')
    for setting in config['settings']:
        preprocess_videos(workspace, setting)

    # Create sub_setups
    logging.info('Creating sub setups...')
    create_sub_setups(workspace)

    # Extract human pose from videos
    logging.info('Extracting human pose from videos...')
    for pose_estimation_config in config['pose_estimation_configs']:
        extract_pose_from_videos(workspace, pose_estimation_config)

    # Organizing the logs by OpenSim
    move_logs_to_workspace(workspace, 'preprocessing')

    logging.info('Done!')
