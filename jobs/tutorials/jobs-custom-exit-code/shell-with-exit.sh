#!/bin/bash
var=$1
if [ -z "$var" ]
then
      echo "no argument provided"
      exit 131
else
      echo "arguments available"
      while [ "$1" != "" ]; do
        echo "Received: ${1}" && shift;
      done
fi