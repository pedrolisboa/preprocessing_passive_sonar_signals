#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PROFILE = default
PROJECT_NAME = preprocessing_passive_sonar_signals
USER_ID = $$(id -u)
USER_GROUP = $$(id -g)
PYTHON_INTERPRETER = python3


#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Build container
build-container: 
	scripts/build_container.sh

## Make Dataset
dataset:
	docker run \
		-it \
		--env-file "${PROJECT_DIR}"/.env \
		-v "${PROJECT_DIR}"/data:/data \
		-v "${PROJECT_DIR}"/scripts:/scripts:ro \
		-u ${USER_ID}:${USER_GROUP} \
		pedrolisboa/theseus:latest \
		$(PYTHON_INTERPRETER) scripts/build_dataset.py

# Generating configuration files
config:
	docker run \
		-it \
		--env-file "${PROJECT_DIR}"/.env \
		-v "${PROJECT_DIR}"/configs:/configs\
		-v "${PROJECT_DIR}"/scripts:/scripts:ro \
		-u ${USER_ID}:${USER_GROUP} \
		pedrolisboa/theseus:latest \
		${PYTHON_INTERPRETER} configs/generator.py --path configs

###################################
# Not implemented yet			  #
###################################
sync:
	scripts/sync_datasets.sh
	scripts/sync_containers.sh
	scripts/sync_configs.sh
	scripts/sync_tasks.sh

run: sync
	${PYTHON_INTERPRETER} scripts/train_models.py --useCluster True

run-local:
	docker run \
		-it \
		--env-file "${PROJECT_DIR}"/.env \
		-v "${PROJECT_DIR}"/data:/data:ro \
		-v "${PROJECT_DIR}"/configs:/configs:ro\
		-v "${PROJECT_DIR}"/models:/models \
		-v "${PROJECT_DIR}"/scripts:/scripts:ro \
		-u ${USER_ID}:${USER_GROUP} \
		pedrolisboa/theseus:latest \
		${PYTHON_INTERPRETER} scripts/train_models.py --useCluster False --jobfileFolder .		

