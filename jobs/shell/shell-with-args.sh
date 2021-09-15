#!/bin/bash
var=$1
if [ -z "$var" ]
then
      echo "no argument provided"
      exit 100
else
      while [ "$1" != "" ]; do
        echo "Received: ${1}" && shift;
      done
fi