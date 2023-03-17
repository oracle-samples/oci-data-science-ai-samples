#!/bin/bash
git version

BASEDIR=$(dirname "$(readlink -f "$0")")

# check for git report
if [ -z "${GIT_REPO}" ]; then
  echo "set default git repo: https://github.com/lyudmil-pelov/standbyjob.git"
  GIT_REPO="https://github.com/lyudmil-pelov/standbyjob.git"
fi

# check for entrypoint, it has to be entrypoint
if [ -z "${ENTRYPOINT}" ]; then
  echo "set default entrypoint: test.py"
  ENTRYPOINT="test.py"
fi

# pull interval in seconds
if [ -z "${PULL_INTERVAL}" ]; then
  echo "set default pull interval of 10 seconds"
  PULL_INTERVAL=10
fi

# set the git repository URL
git_repo=$GIT_REPO

# ...and local directory to checkout the code
local_dir=$BASEDIR/code

# set the main python file to run
main_file=$ENTRYPOINT

# set the interval for pulling (in seconds)
pull_interval=$PULL_INTERVAL

# initialize the last commit hash variable
last_commit=""

# Check if the directory exists, try to create it if it doesn't
if [[ -d "$local_dir" && -n "$(ls -A "$local_dir")" ]]; then
  echo "Sync Directory: $local_dir"
else
  echo "Creating sync directory: $local_dir"
  if mkdir -p "$local_dir"; then
    echo "Sync directory created"
  else
    echo "Error: Unable to create sync directory" >&2
    exit 61
  fi
fi

# check if the local directory is a Git repository
echo "check the local directory has the git repository already..."
if [ -d "$local_dir/.git" ]; then
    # below does not work on older git cli!
    # git -C "$local_dir" pull "$git_repo"
    echo "repository exist!"
else
    # if the directory is not a git repository, clone first
    echo "repository does not exist, clone it!"
    git clone "$git_repo" "$local_dir"
fi

# enter the directory
echo "enter the directory"
cd "$local_dir"
pwd

# loop indefinitely - you could use Job Mac Runtime or Cancel the Job Run
while true; do
    
    # does not work on older git versions!
    # latest_commit=$(git -C "$local_dir" rev-parse HEAD)
    # latest_commit=$(git rev-parse HEAD "$local_dir")
    echo "check latest commit..."
    latest_commit=$(git ls-remote "$git_repo" HEAD)
    echo $latest_commit

    # if the latest commit is different from the last one, run the main python file
    if [ "$latest_commit" != "$last_commit" ]; then
        echo "remote repositori has a change"
        # wait for any previous execution to finish
        while ps aux | grep "$main_file" | grep -v grep > /dev/null; do
            sleep 1
        done
        
        echo "pull the latest version"
        git pull "$git_repo"

        # run the main python file
        # python3 "$local_dir/$main_file"
        python3 "$main_file"
    
        # update the last commit variable
        last_commit="$latest_commit"
    else
      echo "Already up to date"
    fi

    # wait for the specified interval before pulling again
    sleep "$pull_interval"
done
