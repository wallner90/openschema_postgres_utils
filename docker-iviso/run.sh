#!/bin/bash

CONTAINER_NAME="postgres_ait"
if docker container inspect ${CONTAINER_NAME} > /dev/null
then
  echo "Start existing container: ${CONTAINER_NAME}"
  docker start ${CONTAINER_NAME}
else
  echo "Create container: ${CONTAINER_NAME}"
  docker run --name ${CONTAINER_NAME} --net host -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=postgres_alchemy_ait postgres_uuid-ossp_postgis
fi