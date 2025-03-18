#!/bin/bash

echo_command() {
  echo "--------------------------------------------------------"
  echo "TEST: $1"
  echo "--------------------------------------------------------"
}

set -e

ENV="test-production"
if [ -n "$1" ]; then
  ENV="$1"
fi

this_script=$(realpath "$0")
script_dir=$(dirname "$this_script")
cd "$script_dir"

echo_command "BUILD"
./mlapp build

echo_command "DEPLOY"
./mlapp deploy -e "$ENV"

echo_command "INSTANTIATE"
./mlapp instantiate -e "$ENV"

echo_command "SHOW"
./mlapp show -e "$ENV"

echo_command "TRIGGER"
./mlapp trigger -wmd fetalrisk -e "$ENV"

echo_command "PREDICT"
./mlapp predict -e "$ENV"

echo_command "DELETE"
./mlapp undeploy --cascade-delete --force -e "$ENV"
