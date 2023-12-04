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
    sleep 30 # Delay for checking updates
    git -C "${REPO_NAME}" fetch
    LOCAL=$(git -C "${REPO_NAME}" rev-parse @)
    REMOTE=$(git -C "${REPO_NAME}" rev-parse @{u})

    # Check if local is different from remote
    if [ "${LOCAL}" != "${REMOTE}" ]; then
        echo "New commit detected. Updating and running script."
        update_repo
        pkill -f "${REPO_NAME}/${SCRIPT_PATH}" # Kill the running script
        run_script
    fi
done

