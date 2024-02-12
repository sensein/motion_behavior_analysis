"""
Module description: This module contains the main functionality 
for processing the videos (triangulation, association, filtering, etc).
"""

import logging
import logging.handlers
from utility.utils import get_workspace, read_config, move_logs_to_workspace, setup_logging
from utility.processing import process

if __name__ == "__main__":
    # Read workspace
    workspace = get_workspace()

    # Read the configuration file
    config = read_config(workspace)

    # Setup logging
    setup_logging(workspace, 'processing')

    # Processing
    logging.info("Processing...")
    process(workspace, config)

    # Organizing the logs by OpenSim
    move_logs_to_workspace(workspace, 'processing')

    logging.info("Done!")


# TODO: 
# - Fix readme
# - Add new videos to demo
# - Push to github
