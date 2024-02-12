"""
Module description: This module contains a set of utility functions for processing the videos
(triangulation, person association, filtering, etc.).
"""

import logging
import logging.handlers
import os
import glob
import json
from Pose2Sim import Pose2Sim
from utility.utils import find_unique_base_names

def process(workspace, configs):
    """
    Processes the workspace using the provided configurations.

    Args:
        workspace: The workspace directory to be calibrated.
        configs: The configurations to be used.

    Returns:
        None
    """
    subproject_folders = get_subproject_dirs(workspace)
    for subproject_folder in subproject_folders:
        for i in range(len(configs['pose_estimation_configs'])):
            for j in range(len(configs['filtering']['filters'])):               
                config_dict = prepare_processing_config_dict(subproject_folder, configs, i, j)
                """
                retry = True
                while retry:
                    try:
                        run_person_association(config_dict)
                        retry = False
                    except Exception:
                        config_dict = adapt_config(config_dict, "person_association")
                """

                retry = True
                while retry:
                    try:
                        run_triangulation(config_dict)
                        retry = False
                    except Exception:
                        config_dict = adapt_config(config_dict, "triangulation")

                try: 
                    run_filtering(config_dict)
                except Exception as e:
                    logging.error(f"Error in filtering with filter {config_dict['filtering']['type']}")
                    # logging.error(e)
                    
                #run_kinematics(subproject_folder)
                save_config(config_dict)                   

def save_config(config_dict):
    """
    Save the config dictionary to a JSON file.

    Args:
        config_dict (dict): The dictionary containing the configuration parameters.

    Returns:
        None
    """
    with open(os.path.join(config_dict['project']['project_dir'], 'pose-3d', 
                           f"actual_processing_config_{config_dict['pose']['pose_model']}_{config_dict['filtering']['type']}.json"), 
              'w', 
              encoding='utf-8') as f:
        json.dump(config_dict, f, indent=4)

def adapt_config(config_dict, phase):
    """
    Function to adapt the configuration dictionary based on the given phase.

    Args:
        config_dict (dict): The original configuration dictionary.
        phase (str): The phase for which the configuration needs to be adapted.

    Returns:
        dict: The adapted configuration dictionary.
    """
    if phase == "person_association":
        config_dict['personAssociation']['reproj_error_threshold_association'] = (
            config_dict['personAssociation']['reproj_error_threshold_association'] + 10
        )
    else: 
        config_dict['triangulation']['reproj_error_threshold_triangulation'] = (
            config_dict['triangulation']['reproj_error_threshold_triangulation'] + 10
        )
        config_dict['triangulation']['interp_if_gap_smaller_than'] = (
            config_dict['triangulation']['interp_if_gap_smaller_than'] + 10
        )
    return config_dict

def run_person_association(configs):
    """
    Function to run person association using the provided configurations.

    Args:
    - configs: A dictionary containing project configurations.

    Returns:
    - None
    """
    project_dir = configs['project']['project_dir']
    pose_associated_path = os.path.join(project_dir, "pose-associated")   
    if (os.path.exists(pose_associated_path) and 
        os.path.isdir(pose_associated_path)):    
        cameras = list(find_unique_base_names(project_dir))
        count = 0
        for camera in cameras:
            pose_framework = configs['pose']['pose_framework']
            pose_model = configs['pose']['pose_model']
            camera_json_path = os.path.join(pose_associated_path, f"blaze_{camera}_json")         
            if (pose_framework == 'mediapipe' and 
                pose_model == 'BLAZEPOSE' and 
                os.path.exists(camera_json_path)):
                count += 1  
        if count == len(cameras):
            return           
    # Person association
    Pose2Sim.personAssociation(configs)
    return

def run_triangulation(config_dict):
    """
    A function to run triangulation using the provided configuration dictionary.

    Parameters:
    config_dict (dict): The dictionary containing configuration parameters.

    Returns:
    None
    """
    model_name = config_dict['pose']['pose_model']
    project_dir = config_dict['project']['project_dir']
    pattern = f"actual_processing_config_{model_name}_*.json"

    # Search for any file that matches the pattern regardless of the filter_name
    matching_files = glob.glob(os.path.join(project_dir, 'pose-3d', pattern))

    # If there is at least one matching file, return
    if matching_files:
        return

    # Triangulation
    Pose2Sim.triangulation(config_dict)

def run_filtering(config_dict):
    """
    A function to run filtering based on the provided configuration dictionary.
    Param:
        config_dict: A dictionary containing configuration parameters for filtering.
    Return:
        None
    """
    # Filtering

    model_name = config_dict['pose']['pose_model']
    filter_name = config_dict['filtering']['type']
    project_dir = config_dict['project']['project_dir']
    pattern = f"actual_processing_config_{model_name}_{filter_name}.json"

    # Search for any file that matches the pattern regardless of the filter_name
    matching_files = glob.glob(os.path.join(project_dir, 'pose-3d', pattern))

    # If there is at least one matching file, return
    if matching_files:
        return

    Pose2Sim.filtering(config_dict)

def get_subproject_dirs(workspace):
    """
    Get subproject directories within the given workspace.

    Args:
        workspace: The path to the workspace directory.

    Returns:
        List: A list of subproject directory paths.
    """
    subproject_folders = []
    for root, dirs, _ in os.walk(workspace):
        if ("pose" in dirs and 
            ("__synced__" in root and not "unset_unset_unset_unset" in root) and 
            os.path.exists(os.path.join(root, '..', '..', 'Calibration', 'Calib_board.toml'))):
            subproject_folders.append(root)
    return subproject_folders

def prepare_processing_config_dict(subproject_folder, configs, i, j):
    """
    Prepare subproject config dictionary.

    Args:
        subproject_folder: The subproject folder.
        processing_configs: The processing configurations.

    Returns:
        dict: The subproject config dictionary.
    """

    subproject_config_dict = {
        "project": {
            "project_dir": subproject_folder,
            "frame_range": [], 
            "frame_rate": extract_fps(subproject_folder),
        },
        "personAssociation": {
            "single_person": True, 
            "tracked_keypoint": configs['person_association']['tracked_keypoint'], 
            "reproj_error_threshold_association": 
            configs['person_association']['reproj_error_threshold_association'], 
            "likelihood_threshold_association": 
            configs['person_association']['likelihood_threshold_association'],
        }, 
        "pose": {
            "pose_framework": configs['pose_estimation_configs'][i]['pose_framework'],
            "pose_model": configs['pose_estimation_configs'][i]['pose_model'],
        }, 
        "triangulation": {
            "reproj_error_threshold_triangulation": 
            configs['triangulation']['reproj_error_threshold_triangulation'],
            "likelihood_threshold_triangulation": 
            configs['triangulation']['likelihood_threshold_triangulation'],
            "min_cameras_for_triangulation": 
            configs['triangulation']['min_cameras_for_triangulation'],
            "interpolation": configs['triangulation']['interpolation'],
            "interp_if_gap_smaller_than": configs['triangulation']['interp_if_gap_smaller_than'],
            "show_interp_indices": configs['triangulation']['show_interp_indices'],
            "handle_LR_swap": configs['triangulation']['handle_LR_swap'],
            "undistort_points": configs['triangulation']['undistort_points']
        }, 
        "filtering": {
            "display_figures": configs['filtering']['display_figures'],
            "type": list(configs['filtering']['filters'])[j],
            "butterworth": {
                "order": configs['filtering']['filters']['butterworth']['order'],
                "cut_off_frequency": configs['filtering']['filters']['butterworth']['cut_off_frequency'],
            },
            "kalman": {
                "trust_ratio": configs['filtering']['filters']['kalman']['trust_ratio'],
                "smooth": configs['filtering']['filters']['kalman']['smooth'],
            },
            "butterworth_on_speed": {
                "order": configs['filtering']['filters']['butterworth_on_speed']['order'],
                "cut_off_frequency": configs['filtering']['filters']['butterworth_on_speed']['cut_off_frequency'],
            },
            "gaussian": {
                "sigma_kernel": configs['filtering']['filters']['gaussian']['sigma_kernel'],
            },
            "LOESS": {
                "nb_values_used": configs['filtering']['filters']['LOESS']['nb_values_used'],
            },
            "median": {
                "kernel_size": configs['filtering']['filters']['median']['kernel_size'],
            },
        }
    }
    
    return subproject_config_dict

def extract_fps(folder_name, default=30):
    """
    Extracts the frames per second (FPS) from the given folder name.

    Args:
        folder_name (str): The name of the folder containing the FPS information.
        default (int, optional): The default FPS to return if the FPS is 'unset'. Defaults to 30.

    Returns:
        int: The extracted FPS from the folder name, or the default FPS if 'unset'.
    """

    # Split the folder name by '__synced__'
    parts = folder_name.split('__synced__')

    # Check if the split was successful
    if len(parts) < 2:
        return "Folder path does not contain '__synced__'"

    # Further split the second part by '/' to get subfolders
    subfolders = parts[1].split('/')

    # Check if there are at least two subfolders
    if len(subfolders) < 3:
        return "Not enough subfolders to extract FPS"

    # Split the second subfolder by '_' and extract the first element
    fps = subfolders[2].split('_')[0]

    if fps == 'unset':
        return default
    return int(fps)
