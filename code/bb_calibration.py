"""
Module description: This module contains the main functionality 
for performing camera calibration.
"""

import logging
import logging.handlers
from utility.utils import get_workspace, read_config, move_logs_to_workspace, setup_logging
from utility.calibration import calibrate

if __name__ == "__main__":
    # Read workspace
    workspace = get_workspace()

    # Read the configuration file
    logging.info("Reading the configuration file...")
    config = read_config(workspace)

    # Setup logging
    setup_logging(workspace, 'calibration')

    # Calibration
    logging.info("Calibration...")
    calibrate(workspace, config['calibration_configs'])

    # Organizing the logs by OpenSim
    move_logs_to_workspace(workspace, 'calibration')

    logging.info("Done!")
