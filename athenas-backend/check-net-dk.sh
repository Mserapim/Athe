#!/bin/bash

network_name=$1
max_attempts=10
interval=5

attempt=1

while [ $attempt -le $max_attempts ]
do
  docker network inspect $network_name > /dev/null 2>&1
  if [ $? -ne 0 ]; then
    echo "A rede $network_name foi excluída."
    exit 0
  fi

  echo "A rede $network_name ainda existe. Tentativa $attempt de $max_attempts."

  sleep $interval
  ((attempt++))
done

echo "A rede $network_name não foi excluída após $max_attempts tentativas."
exit 1
