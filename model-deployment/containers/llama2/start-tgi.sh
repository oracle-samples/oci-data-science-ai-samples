#!/bin/bash 

export HUGGING_FACE_HUB_TOKEN=$(cat $TOKEN_FILE)

echo "Checking internet connection: "

curl -sI -v https://www.wikipedia.org
# echo "Downloading weights:"

# text-generation-server download-weights $MODEL_ID

# echo "Download complete"
echo $(du -sh /home/datascience/*)

echo "starting nginx server and TGI"
nginx -p $PWD && text-generation-launcher --json-output $PARAMS

echo "Exiting TGI. Here is the disk utilization of /home/datascience - "
echo $(du -sh /home/datascience)
 
exit $LastExitCode

