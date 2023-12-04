#!/bin/bash

echo "Initilize git checkout"

# Check for required environment variables
if [ -z "${GIT_REPO_URL}" ]; then
    echo "Error: Environment variable GIT_REPO_URL is not set."
    exit 1
fi

if [ -z "${GIT_SCRIPT_PATH}" ]; then
    echo "Error: Environment variable GIT_SCRIPT_PATH is not set."
    exit 1
fi

# Environment variables
REPO_URL="${GIT_REPO_URL}"
SCRIPT_PATH="${GIT_SCRIPT_PATH}"

# Clone or update repository function
update_repo() {
    if [ ! -d "${REPO_NAME}" ]; then
        git clone "${REPO_URL}"
    else
        git -C "${REPO_NAME}" pull
    fi
}

# Run script from repository function
run_script() {
    /bin/bash "${REPO_NAME}/${SCRIPT_PATH}" &
    echo $! > script_pid
}

echo "set repo base name"
# Get the name of the repo from URL
REPO_NAME=$(basename "${REPO_URL}" .git)

# Initial clone or pull
echo "clone repo"
update_repo
echo "run script"
run_script

# Monitoring loop
while true; do
    sleep 30
    git -C "${REPO_NAME}" fetch
    LOCAL=$(git -C "${REPO_NAME}" rev-parse @)
    REMOTE=$(git -C "${REPO_NAME}" rev-parse @{u})

    # Check if local is different from remote
    if [ "${LOCAL}" != "${REMOTE}" ]; then
        echo "New commit detected. Updating and running script."
        update_repo
        echo "kill the running script"
        # pkill -f "${REPO_NAME}/${SCRIPT_PATH}" # Kill the running script
        # kill $(cat script_pid)
        # Kill the script using PID from script_pid
        kill $(cat script_pid)

        # Kill all 'vllm' processes
        ps aux | grep 'vllm' | awk '{print $2}' | xargs -r kill

        # Kill all ray cluster processes
        ps aux | grep 'ray' | awk '{print $2}' | xargs -r kill

        # Function to wait for process to terminate
        wait_for_process_end() {
            local pid=$1
            local timeout=$2
            local wait_interval=1
            local elapsed_time=0

            while kill -0 "$pid" 2> /dev/null; do
                echo "Waiting for process $pid to terminate..."
                sleep $wait_interval
                elapsed_time=$((elapsed_time + wait_interval))
                if [ $elapsed_time -ge $timeout ]; then
                    echo "Process $pid did not terminate within $timeout seconds. Proceeding anyway."
                    break
                fi
            done
        }

        # Wait for processes to terminate
        for pid in $(cat script_pid) $(ps aux | grep 'vllm' | awk '{print $2}') $(ps aux | grep 'ray' | awk '{print $2}'); do
            wait_for_process_end $pid 30
        done

        echo "All processes terminated. Continuing with the next part of the script."        
        echo "Run the script again"
        run_script
    fi
done

