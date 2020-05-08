# Preprocessing Passive Sonar Signals

## Setup configuration

In order to start running the experiments on this repository, place the acoustic lane dataset on the following path

``` bash
<repository_path>/data/raw/4classes
```

Create a .env file inside the cloned repository with the following enviroment variables set to the dockerhub and cluster username. Even if the models are going to be trained locally, the cluster username
will be used to name the configuration and results folders.

``` bash
# .env file
DOCKERHUB = <dockerhub_username>
CLUSTER_USER = <cluster_username>
```

Running the tasks on lps cluster requires [maestro](https://github.com/gabriel-milan/maestro) configuration. Follow the [documentation](https://maestro-lps.readthedocs.io/en/latest/#support)

## Commands

### Build the docker image

``` bash
$ make build-container

```

### Generate training configurations

``` bash
make config
```

### Generate hdf5 datafile for the acoustic lane dataset

``` bash
make dataset
```

### Upload the configuration folder and datset to the lps cluster (not implemented yet, follow the maestro documentation)

``` bash
make sync
```

### Running experiments

Run the following script to send the tasks to the cluster (do not forget to change the user and namespaces inside the script)

``` bash
make run

```

To execute the tasks locally, run the following

``` bash
make run-local
```
