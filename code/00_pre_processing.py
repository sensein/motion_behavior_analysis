from utility.sync import *
from utility.preprocess import *
from utility.human_pose_estimation import *

if __name__ == "__main__":
    # Read workspace
    workspace = get_workspace()

    # Read the configuration file
    config = read_config(workspace)

    # Sync the videos
    sync_videos(workspace)

    # Preprocess videos based on the settings in the config file
    for setting in config['settings']:
        preprocess_videos(workspace, setting)

    # Create sub_setups
    create_sub_setups(workspace)

    # Extract human pose from videos
    for pose_estimation_config in config['pose_estimation_configs']:
        extract_pose_from_videos(workspace, pose_estimation_config)

    print("Done!")