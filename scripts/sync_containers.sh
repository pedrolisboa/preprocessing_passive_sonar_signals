# Must be pushed for lps cluster use
export $(egrep -v '^#' $1.env) 

docker push ${DOCKERHUB}/theseus:$1
docker push ${DOCKERHUB}/theseus:latest
