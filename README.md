# Decision Trees for Anomaly Detection in Smart Factory Processes

## Overview

This project involves training a decision tree classifier and a k-NN classifier. The data undergoes several stages of cleaning and preparation before being used to train and test the models.


### Prerequisites

- Python 3.x & Libraries Pandas, Scikit-learn, Matplotlib
- Docker Desktop

### Clone the repository:

   `git clone https://github.com/aehilsthenomad/decision-trees-for-anomaly-detection.git`\
   `cd decision-trees-for-anomaly-detection`

### Data
data/raw/operation_log.csv: The raw dataset.\
data/processed/clean_operation_log.csv: The cleaned dataset.\
data/processed/prepared_operation_log.csv: The prepared dataset ready for model training.\

### Guide
1. Build a Docker container image.\
   The most standard and recommended way to create a Docker image is by writing a Dockerfile that defines the steps needed to build the image.\
   You will use this command  to create a Docker image from a Dockerfile located in your current directory.\
   docker build: Initiates the image building process -- `docker build -t [imagename]:[tag] .`
   
   `-t [imagename]:[tag]`: Tags the resulting image with a name and tag. Tags are a way to version your images. 'latest' is a commonly used tag to indicate the most recent version of an image, but you can use any tag that suits your versioning strategy (e.g., v1.0, release, stable).\
   `.`: Defines the build context. By specifying `.` (the current directory), you tell Docker to use the current directory's contents to build the image. This directory should include a Dockerfile, which contains the instructions on how to build the image.
   
3. Create and run a new container from this image using\
	`docker run -it --name [containername] -v /host/path:/container/path [imagename]`

    docker run: The command to create and run a new container.\
    `-it`: This makes the container interactive, allocating a pseudo-TTY and keeping stdin open.\
    `--name [containername]`: This names the container.\
    `-v /host/path:/container/path`: This mounts a volume, mapping /host/path on the host to /container/path inside the container. Replace these paths with the actual paths you intend to use.\
    `[imagename]`: This specifies the image to use.
   
    Note: Using a mounted volume allows you to persist data generated or used by a container outside of the container's filesystem, enabling data sharing between the host and the container and preserving data even if the container is removed or recreated.\

4. In terminal, execute container with\
    `docker exec -it  [containername] /bin/bash`\
    `cd app`
5. Run factory script with\
    `python3 opcua\baking\factory.py`
6. To run client script, open a new shell in terminal. Repeat step 3, followed by\
    `python3 opcua\baking\client.py`

You will use `client.py` to interact with `factory.py` and `recipe.py` to create and manage recipe objects through a simple menu interface. The `recipe.py` file contains the recipe classes for Croissants, Pies, and Cookies. When you run `client.py`, a menu appears, allowing you to set the process state, specify or change recipes, raise continuous or state anomalies to test the system, or exit the program. When you select an option, `client.py` uses the Factory class in `factory.py` to select the appropriate recipe object according to the user's choice, which is then displayed. This setup allows you to easily extend the program with new types of recipes without changing the core logic in `client.py`.

### Acknowledgements

This project includes code from another repository: https://github.com/exalens/factory-sim.git

Files client.py, factory.py, and recipe.py were originally retrieved from this repository. Significant changes have been made to client.py and factory.py, while recipe.py remains largely unchanged but is necessary for the functionality of the simulation.

### License
This project is licensed under the GNU General Public License v3.0. See the LICENSE file for more details.

### Contact
For inquiries please contact okara.elisha@gmail.com
