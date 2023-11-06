#!/bin/bash

# Re-Run Duration
sleep_duration=10

# period run every sleep_duration seconds
while true; do
  rclone sync /home/datascience/mybucket/ remote:dtv15/
  sleep $sleep_duration
done
