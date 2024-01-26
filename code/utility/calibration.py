import os
import time
import logging, logging.handlers
from Pose2Sim.calibration import calibrate_cams_all
from Pose2Sim.Pose2Sim import setup_logging

def calibrate(workspace, calibration_configs):
    """
    Calibrates the workspace using the provided calibration configurations.

    Args:
        workspace: The workspace directory to be calibrated.
        calibration_configs: The calibration configurations to be used.

    Returns:
        None
    """
    subproject_folders = get_subproject_dirs(workspace)
    for subproject_folder in subproject_folders:
        calibration_results_file = os.path.join(subproject_folder, 'Calibration', 'Calib_board.toml')
        if not os.path.exists(calibration_results_file) or (os.path.exists(calibration_results_file) and calibration_configs['overwrite']):
            subproject_config_dict = prepare_subproject_config_dict(subproject_folder, calibration_configs)
            calibration(subproject_config_dict)

def get_subproject_dirs(workspace):
    """
    Get subproject directories within the given workspace.

    Args:
        workspace: The path to the workspace directory.

    Returns:
        List: A list of subproject directory paths.
    """
    subproject_folders = []
    for root, dirs, files in os.walk(workspace):
        if "Calibration" in dirs and ("__synced__" in root and not "unset_unset_unset_unset" in root):
            subproject_folders.append(root)
    return subproject_folders

def prepare_subproject_config_dict(subproject_folder, calibration_configs):
    """
    Prepare subproject config dictionary.

    Args:
        subproject_folder: The subproject folder.
        calibration_configs: The calibration configurations.

    Returns:
        dict: The subproject config dictionary.
    """
    subproject_config_dict = {
        "project": {
            "project_dir": subproject_folder
        },
        "calibration": {
            "calibration_type": "calculate",
            "calculate": {
                "intrinsics": {
                    "overwrite_intrinsics": calibration_configs['intrinsics']['overwrite_intrinsics'],
                    "show_detection_intrinsics": calibration_configs['intrinsics']['show_detection_intrinsics'],
                    "intrinsics_extension": calibration_configs['intrinsics']['intrinsics_extension'],
                    "extract_every_N_sec": calibration_configs['intrinsics']['extract_every_N_sec'],
                    "intrinsics_corners_nb": calibration_configs['intrinsics']['intrinsics_corners_nb'],
                    "intrinsics_square_size": calibration_configs['intrinsics']['intrinsics_square_size']
                },
                "extrinsics": {
                    "calculate_extrinsics": calibration_configs['extrinsics']['calculate_extrinsics'],
                    "extrinsics_method": "board",
                    "board": {
                        "show_reprojection_error": calibration_configs['extrinsics']['show_reprojection_error'],
                        "extrinsics_extension": calibration_configs['extrinsics']['extrinsics_extension'],
                        "extrinsics_corners_nb": calibration_configs['extrinsics']['extrinsics_corners_nb'],
                        "extrinsics_square_size": calibration_configs['extrinsics']['extrinsics_square_size']
                    }
                }
            }
        }
    }
    return subproject_config_dict

def calibration(config=None):
    '''
    Cameras calibration from checkerboards files. Adapted from Pose2Sim.calibration, which wants the calibration script to be in the same directory of the data
    
    config can be a dictionary
    '''

    # Set up logging
    session_dir = config['project']['project_dir']
    setup_logging(session_dir)  
    
    # Run calibration
    calib_dir = [os.path.join(session_dir, c) for c in os.listdir(session_dir) if ('Calib' or 'calib') in c][0]
    logging.info("\n\n---------------------------------------------------------------------")
    logging.info("Camera calibration")
    logging.info("---------------------------------------------------------------------")
    logging.info(f"\nCalibration directory: {calib_dir}")
    start = time.time()
    
    calibrate_cams_all(config)
    
    end = time.time()
    logging.info(f'Calibration took {end-start:.2f} s.')