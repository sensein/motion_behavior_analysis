# Motion behavior analysis
## Overview
This repository provides code for automatic video-based analysis of motor control, leveraging the framework established by [Pose2Sim](https://github.com/perfanalytics/pose2sim). Pose2Sim introduces a method for 3D markerless kinematics, offering an alternative to traditional marker-based motion capture techniques. It aims to deliver a cost-effective solution for achieving research-quality outcomes using everyday recording devices such as smartphones, webcams, and GoPros.

As of now, this repository includes functionalities for synchronizing videos through audio spike detection, preprocessing videos for resampling and resolution adjustment, extracting 2D poses using Mediapipe (BlazePose), and ultimately generating OpenSim results, which detail full-body 3D joint angles. This suite of tools facilitates the evaluation of different camera setups for human pose tracking in space, enabling comparisons of results derived from varying video qualities.

## Repository Structure
The repository is organized into several key directories and files:

- ```code/```: Contains all the source code.
- ```data/```: Includes data with a specific hierarchy.
- ```docs/```: Documentation and related materials.
- ```results/```: Output results and analysis reports.


## Installation
To set up the project environment:

- Clone the repository.
- Create a conda env:
````
conda create -n mba python=3.8
````
- Activate the env:
````
conda activate mba
````
- Install required dependencies:
````
pip install -r requirements.txt
````

## Usage
To run the main analysis:

- Populate the data folder respecting the hierarchy
- Navigate to the ```code/``` directory.
- Execute the scripts:
````
python aa_pre_processing.py --workspace ../data/sessions
python bb_calibration.py --workspace ../data/sessions
python cc_processing.py --workspace ../data/sessions
````

## Expectations
As a demo, from the videos from [camera 1](https://github.com/sensein/motion_behavior_analysis/blob/main/data/sessions/S1/original/all_cams/unset_unset_unset_unset/P1/T2/raw/cam3.mov) and [camera 2](https://github.com/sensein/motion_behavior_analysis/blob/main/data/sessions/S1/original/all_cams/unset_unset_unset_unset/P1/T2/raw/cam2.mov) we can obtain [OpenSim kinematics](https://github.com/sensein/motion_behavior_analysis/blob/main/opensim.mp4). 


## Contributing
Contributions are welcome. Please refer to ```CONTRIBUTING.md``` for guidelines.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
Thank you.