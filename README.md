# Motion behavior analysis
## Overview
This repository contains the code for the automatic motion behavior analysis.

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
python 00_pre_processing.py
python 01_calibration.py
python 02_processing.py
````

## Contributing
Contributions are welcome. Please refer to ```CONTRIBUTING.md``` for guidelines.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
Thank you.