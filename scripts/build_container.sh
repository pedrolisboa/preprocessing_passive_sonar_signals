#!/bin/bash

scriptpath=$(dirname $(readlink -f $BASH_SOURCE))
cd $scriptpath
cd ../ 
# for the building to work properly, we must run it on the base directory of the repository

docker build -t pedrolisboa/theseus:$1 ./container
docker build -t pedrolisboa/theseus:latest ./container
docker push pedrolisboa/theseus:$1
docker push pedrolisboa/theseus:latest
