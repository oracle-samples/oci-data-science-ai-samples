#!/bin/bash
 
# Set variables
REMOTE_REPO="<remote_repository>"  # Replace with the URL of your remote Git repository
BRANCH="<branch_name>"             # Replace with the name of the branch you want to push changes to
COMMIT_MESSAGE="<commit_message>"  # Replace with the commit message you want to use
CLONE_DIR="path/to/local/repor"    # Replace with the commit message you want to use
 
cd $CLONE_DIR
 
# Check if there are any changes
if [[ $(git status --porcelain) ]]; then
  # Changes detected, commit and push
  git add .
  git commit -m "$COMMIT_MESSAGE"
  git push $REMOTE_REPO $BRANCH
else
  # No changes detected
  echo "No changes detected."
fi