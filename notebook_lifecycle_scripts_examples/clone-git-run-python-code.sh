#!/bin/bash
 
# Set variables
REPO_URL="https://github.com/user/repo.git" # Replace with the URL of the repository you want to clone
CLONE_DIR="$HOME/path/to/clone/dir" # Replace with the path of the directory where you want to clone the repository
FILE_TO_RUN="file.sh" # Replace with the name of the file you want to run
 
# Check if the directory exists, try to create it if it doesn't
if [[ -d "$CLONE_DIR" && -n "$(ls -A "$CLONE_DIR")" ]]; then
  echo "Clone Directory: $CLONE_DIR"
else
  echo "Creating clone directory: $CLONE_DIR"
  if mkdir -p "$CLONE_DIR"; then
    echo "Sync directory created"
  else
    echo "Error: Unable to create sync directory" >&2
    exit 61
  fi
fi
 
 
git clone $REPO_URL $CLONE_DIR
 
# Change directory to the cloned repository
cd $CLONE_DIR
 
# Run the specified file
python $FILE_TO_RUN