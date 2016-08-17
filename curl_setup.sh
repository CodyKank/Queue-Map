#!/bin/bash

#Script to set up the CRC Queue heat-map. Thats what it's called I guess.
#8/3/16
#Requires sudo permission. This script assumes you have apache2 running and 
#php7.0(or something compatible). Default path is listed below.

#This needs to be an absolute path
desired_path="/var/www/html" #you can change this if need be

#CRC info to gather files
webpage_url="URL FOR CRC FILES HERE"

#Local info to mv files to protected areas
psword="LOCAL (WEBSERVER) SUDO PASSWORD"
long_file="long_nodes.txt" #These can stay this way
debug_file="debug_nodes.txt" # "

#Creating dirs moving files to proper locations
echo "Creating Debug, Long, and Pending directories in $desired_path . . ."

echo $psword | sudo -S mkdir $desired_path/Debug
echo $psword | sudo -S mkdir $desired_path/Long
echo $psword | sudo -S mkdir $desired_path/Pending

echo "Moving index's to their rightful places . . ."
echo $psword | sudo -S cp index-long.php $desired_path/Long/index.php
echo $psword | sudo -S cp index-debug.php $desired_path/Debug/index.php
echo $psword | sudo -S cp index-pending.php $desired_path/Pending/index.php

echo "Transferring templates to $desired_path . . ."
echo $psword | sudo -S cp -r templates $desired_path/templates

echo "Transferring styles.css to $desired_path . . ."
echo $psword | sudo -S cp styles.css $desired_path/

echo "Gathering node-list files from $webpage_url . . ."
curl -o debug_nodes.txt $webpage_url/debug_node_list.html
curl -o long_nodes.txt $webpage_url/long_node_list.html

# Creating and initialiizing each node's dir etc
#Long-queue nodes
echo "Creating each node's dir at $desired_path/Long . . ."
while IFS= read -r line
do
        echo $psword | sudo -S mkdir $desired_path/Long/$line
        echo $psword | sudo -S cp sub-index.php $desired_path/Long/$line/index.php
done < "$long_file"

echo "Creating each node's dir at $desired_path/Debug . . ."

#Debug-queue nodes
while IFS= read -r line
do
        echo $psword | sudo -S mkdir $desired_path/Debug/$line
        echo $psword | sudo -S cp sub-index.php $desired_path/Debug/$line/index.php
done < "$debug_file"


echo "-----------------------COMPLETE-----------------------"
echo ""

echo "Setup complete. Please quickly verify everything was made correctly."
echo "You can do this by opening a browser and going to localhost and navigating"
echo "to your Long or Debug directories."
echo ""
echo "Please be sure that the python script is running on a front end, and that"
echo "all scripts are configured to the location the script is going to be spitting"
echo "out at."
echo ""
echo "Once you know things are where they should be, make sure you configured the"
echo "grab_queue_files.sh script for your info to grab the files."
echo "If it is configured already, either of the two lines to crontab -e:"
echo "If you chose method(1) as described in README, add this to cron:"
echo "*/2 * * * * $(pwd)/grab_queue_files.sh"
echo ""
echo "If you chose method(2), add this to cron:"
echo "*/2 * * * * $(pwd)/curl_queue_files.sh"
