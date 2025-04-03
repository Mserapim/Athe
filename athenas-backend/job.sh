#!/bin/bash

ENV=$1
SERVICE=$2

echo $ENV
echo $SERVICE

shift
shift

container=$(docker container ls --filter name=${ENV}_${SERVICE} --format "{{.ID}}")

docker exec -t --user "${UID}" ${container} $@
