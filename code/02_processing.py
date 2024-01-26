from utility.utils import *
from utility.processing import *

if __name__ == "__main__":
    # Read workspace
    workspace = get_workspace()

    # Read the configuration file
    config = read_config(workspace)

    # Calibration
    # calibrate(workspace, config['calibration_configs'])

    """
    # Person association
    if not os.path.exists(os.path.join(project_dir, "pose-associated")) or not os.path.isdir(os.path.join(project_dir, "pose-associated")):
        Pose2Sim.personAssociation(config_dict)

    # Triangulation and Filtering
    if not os.path.exists(os.path.join(project_dir, "pose-3d")) or not os.path.isdir(os.path.join(project_dir, "pose-3d")):
        # Triangulation
        Pose2Sim.triangulation(config_dict)

        # Filtering
        config_dict['filtering']['display_figures'] = True # This is to show how we can dinamically change params
        Pose2Sim.filtering(config_dict)

    # Kinematics (I have't tried it yet through python) # TODO!!
    # Pose2Sim.kinematics(config_dict)    
    """

    print("Done!")



