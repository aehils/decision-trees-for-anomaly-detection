# Decision Trees for Anomaly Detection in Smart Factory Processes

## Overview

This project involves training two binary classifiers: a decision tree and a k-Nearest Neighbours. Data is generated from logs built into an instance of Exalens' factory simulation. The dataset undergoes several stages of cleaning and preparation before being used to train and test the models.


### Prerequisites

- Python 3.x & Install Python libraries Pandas, Scikit-learn, Matplotlib
- Docker Desktop

### Clone the repository:

   `git clone https://github.com/aehilsthenomad/decision-trees-for-anomaly-detection.git`\
   `cd decision-trees-for-anomaly-detection`

### Data
The data goes through 3 stages: generated, cleaned and then prepared for training.

The raw dataset -- data/raw/operation_log.csv\
The cleaned dataset -- data/processed/clean_operation_log.csv\
The prepared dataset ready for model training -- data/processed/prepared_operation_log.csv

## Guide to running the app
1. Build a Docker container image.\
   The recommended way to create a Docker image for this task is by writing a basic Dockerfile that defines the steps needed to build the image.

    Docker provides comprehensive documentation on how to create a Dockerfile suitable for a python application here:\
   https://docs.docker.com/get-started/docker-concepts/building-images/writing-a-dockerfile/

   There is also documentation on how you will build your container image from this Dockerfile, available here: https://docs.docker.com/get-started/docker-concepts/building-images/build-tag-and-publish-an-image/

   In short, you will use this command to create a Docker image from a Dockerfile located in your current directory.\
   `docker build -t [imagename]:[tag] .`
   
3. Initialise a new container from this image using\
	`docker run -it --name [containername] -v /host/path:/container/path [imagename]`

    To learn more about how this command works refer to https://docs.docker.com/engine/containers/run/#:~:text=Docker%20runs%20processes%20in%20isolated,tree%20separate%20from%20the%20host.\
   
    Note: Using a mounted volume allows you to persist data generated or used by a container outside of the container's filesystem, enabling data sharing between the host and the container and preserving data even if the container is removed or recreated.\
   What this means for you is that you can make changes to the files in you source folder and not have to run a new container each time you make a change.

4. In terminal, execute your container and navigate to the directory where the application is located (literally called app, use `ls` to see) with\
    `docker exec -it  [containername] /bin/bash`\
    `cd app`
5. Time to start the factory simulation! Run factory script with\
    `python3 opcua\baking\factory.py`
6. Now to run the client where you will control the simulation, i.e.  start/stop, inject anomalies and more. Open a new shell in terminal. Repeat step 3 to execute container and enter the app, followed by\
    `python3 opcua\baking\client.py`

You will use `client.py` to interact with `factory.py` and `recipe.py` to create and manage recipe objects through a simple menu interface. The `recipe.py` file contains the recipe classes for Croissants, Pies, and Cookies. When you run `client.py`, a menu appears, allowing you to set the process state, specify or change recipes, raise continuous anomalies to test the system, or exit the program. When you select an option, `client.py` uses the Factory class in `factory.py` to select the appropriate recipe object according to the user's choice, which is then displayed. This setup allows you to easily extend the program with new types of recipes without changing the core logic in `client.py`.

### Injecting Anomalies
Anomaly coordinates are displayed in the client shell when injected. You will specify the duration of the irregular data injection.


### Acknowledgements

This project includes code modified from another repository: https://github.com/exalens/factory-sim.git

Files client.py, factory.py, and recipe.py were originally retrieved from this repository. Significant changes have been made to client.py and factory.py, while recipe.py remains largely unchanged but is necessary for the functionality of the simulation.

### License
This project is licensed under the GNU General Public License v3.0. See the LICENSE file for more details.

### Contact
For inquiries please contact okara.elisha@gmail.com
