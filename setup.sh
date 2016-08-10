#!/bin/bash

#Script to set up the CRC Queue heat-map. Thats what it's called I guess.
#8/3/16
#Requires sudo permission. This script assumes you have apache2 running and 
#php7.0(or something compatible). Default path is listed below.

#This needs to be an absolute path
desired_path="/var/www/html" #you can change this if need be

#CRC info to gather files
usename="CRCUSERNAME HERE!"
dest="crcfe01.crc.nd.edu"
pword="CRC-PASSWORD HERE"
path_to_long_file="ABSOLUTE PATH TO long_node_list.html"
path_to_debug_file="ABSOLUTE PATH TO debug_node_list.html"

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

echo "Gathering node-list files from $dest as $usename . . ."
sshpass -p "$pword" scp $usename@$dest:$path_to_long_file $(pwd)/$long_file
sshpass -p "$pword" scp $usename@$dest:$path_to_debug_file $(pwd)/$debug_file

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
echo "If it is configured already, add this line to crontab -e:"
echo "*/2 * * * * $(pwd)/grab_queue_files.sh"
