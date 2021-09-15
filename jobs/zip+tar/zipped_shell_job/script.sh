#!/bin/bash

set -e

BASEDIR=$(dirname "$0")

#read base dir and then import directories. Re pack the scripts into tar and zip both
source $BASEDIR/root-dependency.sh
source $BASEDIR/dependencies/child-dependency.sh
source $BASEDIR/dependencies/dependency/dependency.sh

echo "Calling an external shell function.."
Function