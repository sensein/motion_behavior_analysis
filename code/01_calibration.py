from utility.utils import *
from utility.calibration import *

if __name__ == "__main__":
    # Read workspace
    workspace = get_workspace()

    # Read the configuration file
    config = read_config(workspace)

    # Calibration
    calibrate(workspace, config['calibration_configs'])

    print("Done!")