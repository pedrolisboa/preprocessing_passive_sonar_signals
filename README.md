# Preprocessing Passive Sonar Signals

## Build the docker image


``` bash
$ source scripts/build_container.sh

```

## Running models on lps-cluster

#### First follow the instructions on https://maestro-lps.readthedocs.io/en/latest/#support to have maestro up and running on your machine

#### Generate training configurations (this step is temporary and may face some issues regarding python dependenies).It will be further placed insider a docker exectution enviroment)

``` bash
python3 configs/generator.py
```

#### Generate hdf5 datafile for the acoustic lane dataset (this step is temporary and may face some issues regarding python dependenies).It will be further placed insider a docker exectution enviroment)

``` bash
python3 build_dataset.py
```

#### Upload the configuration folder and datset to the lps cluster

#### Run the following script to send the tasks to the cluster (do not forget to change the user and namespaces inside the script)

``` bash
$ python3 scripts/train_models.py

```
