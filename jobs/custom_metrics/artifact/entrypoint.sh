#! /bin/bash

set -eo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Starting metrics submitter"
python "$DIR/metrics_submitter.py" &
PID=$(echo $!)

echo "Starting work"
# Replace this sleep command with your actual job command(s) and/or script invocation(s).
sleep 600

echo "Terminating metrics submitter"
kill $PID
