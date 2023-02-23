#!/bin/bash

# Set a flag to indicate if a termination signal was received
terminate_flag=false

# Catch the termination signal and set the flag to true
trap 'terminate_flag=true' SIGTERM SIGINT INT

# make sure the environment variables are set and code exits immediatly on error
set -eu

# set the current directory
BASEDIR=$(dirname "$0")

# on local run you can stop the process with Ctrl+C
if [[ -z "${JOB_OCID}" ]]; then
    echo "Press Ctrl+C stop the process"
fi

echo "Settings..."
echo $BASEDIR
echo $SYNC_DIR
echo $BUCKET
echo $OB_PREFIX
echo $JOB_OCID

echo "set the local sync director"
export SYNC_DIR=$BASEDIR/$SYNC_DIR
echo $SYNC_DIR

echo "start sync process..."
#bash $BASEDIR/sync.sh & python $BASEDIR/produce-logs.py

# get the individual process, we want to kill all if one of them has an error!
pids=()
bash $BASEDIR/sync.sh &
pids+=($!)
python $BASEDIR/produce-logs.py &
pids+=($!)

for pid in "${pids[@]}"; do
  # Check the termination flag
  if [ "$terminate_flag" = true ]; then
    echo "Termination signal received, exiting loop..."
    exit_code=$?
    for pid in "${pids[@]}"; do
      kill -9 "$pid" 2> /dev/null || :
    done
    exit "$exit_code"
  fi

  # if the processes are running without error don't bother
  if wait $pid; then
    :
  else
    exit_code=$?
    echo "Process exited with $exit_code, killing the rest of sync now."
    for pid in "${pids[@]}"; do
      kill -9 "$pid" 2> /dev/null || :
    done
    exit "$exit_code"
  fi
done

exit_status=$?
echo 'exit status: '$exit_status
exit $exit_status