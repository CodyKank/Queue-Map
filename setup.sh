#!/bin/bash

# Script to setup a Queue-Map.
# Script will create the necesarry directores described in README
# Script MUST BE RAN AS ROOT!!!
# Dec 13, 2016

#Making so errors stop the script
#set -e
# Making sure user is root
if [ "$EUID" -ne 0 ]
then
    echo "Please run this script as root. ( sudo ./setup.sh)"
    echo "Exiting as user is not root (super-user)."
    exit
fi

#This needs to be an absolute path
desired_path="/var/www/html" #you can change this if need be

#CRC info to gather files
webpage_url="http://www.crc.nd.edu/~ckankel/"
setup_file="queue_mapd-setup.txt"

#Creating dirs moving files to proper locations
echo "Creating Queue-Map main directories in $desired_path . . ."

mkdir -p $desired_path/Queue-Map/HG
echo "Queue-Map and HG directoires created. . ."

echo "Getting setup file from web. . ."
curl -o queue_mapd-setup.txt $webpage_url/queue_mapd-setup.txt
echo "Creating dir's for each Host group found in queue_mapd.txt. . ."
while IFS= read -r line
do
    mem="${line}-memory"
    echo $mem
    mkdir -p $desired_path/Queue-Map/HG/$mem
    mkdir -p $desired_path/Queue-Map/HG/$line
    cp index-hg.php $desired_path/Queue-Map/HG/$line/index.php
    cp index-hg.php $desired_path/Queue-Map/HG/$mem/index.php
done < queue_mapd-setup.txt
rm queue_mapd-setup.txt

# There should NOT be any other *.txt files in this directory!!!

echo "Grabbing queue_mapd-nodes.tar.gz and creating dir's for each node. . ."
curl -o queue_mapd-nodes.tar.gz $webpage_url/queue_mapd-nodes.tar.gz
tar -xzf queue_mapd-nodes.tar.gz
# Here, i will be the name of the HG while $line is the name of the node being created
# This loop is self clearning so all *txt files here will be deleted
for i in *.txt;
do
    name=$(basename "$i" .txt)
    while IFS= read -r line
    do
        mem="${name}-memory"
        mkdir -p $desired_path/Queue-Map/HG/$name/$line
        mkdir -p $desired_path/Queue-Map/HG/$mem/$line
        cp index-node.php $desired_path/Queue-Map/HG/$name/$line/index.php
        cp index-node.php $desired_path/Queue-Map/HG/$mem/$line/index.php
    done < $i
    rm $i
done

echo "Making Pending dir etc. . ."
mkdir -p $desire_path/Queue-Map/Pending
cp index-pending.php $desired_path/Queue-Map/Pending/index.php

echo "Transferring templates and styles.css to $desired_path/Queue-Map. . ."
cp -r templates $desired_path/Queue-Map/templates
cp $desired_path/Queue-Map/styles.css



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
echo "grab_files.sh script for your info to grab the files."
echo "If it is configured already, add this lines to sudo crontab -e:"
echo "*/3 * * * * $(pwd)/grab_files.sh"
