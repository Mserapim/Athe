#!/bin/bash

services="daphne celery flower worker minifier"

function _replicas
{
  for service in $(echo $services)
  do
    docker service update ${1}_${service} --replicas=${2}
  done
}

function _usage
{
  echo ""
  echo "modo de uso:"
  echo "  $0 (up|down) stackname"
  echo ""
}

if [ $# -eq 2 ]; then
  case $1 in
    up)
      _replicas $2 1
      ;;
    down)
      _replicas $2 0
      ;;
    *)
      _usage
      ;;
  esac
else
  _usage
fi
