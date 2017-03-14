#!/bin/bash

#Bash script to gather the html files for a Queuemap webpage. It will grab the files from a web-hosted service,
#like the www directory on a CRC front end. This script should be added into sudo's crontab through
# 'sudo crontab -e'.

#Configurable Information
desired_path="/var/www/html" #typicaly /var/www/html  **(you don't need the last '/')**
curl_url="urlForWebHostedFilesHere" #**Don't need last '/'**


# In queuemapd make the setup file be a file that contains only the host groups, to be read in a way like:
# http://stackoverflow.com/questions/30988586/creating-an-array-from-a-text-file-in-bash

# Getting the tar files
curl -o queue_mapd-core.tar.gz $curl_url/queue_mapd-core.tar.gz
# untar and delete it
tar -xzf queue_mapd-core.tar.gz && rm queue_mapd-core.tar.gz
for i in *gz
do
    tar -xzf $i
    for j in *html
    do
        mv $j $desired_path/Queue-Map/HG/$(basename "$i" .tar.gz)/$(basename "$j" .html)/node.html
        echo ""
    done
    rm $i # So we don't have anymore *gz's in the dir
done

# Repeat above process for memory nodes
curl -o queue_mapd-mem.tar.gz $curl_url/queue_mapd-mem.tar.gz
for i in *gz
do
    tar -xzf $i
    for j in *html
    do
        mv $j $desired_path/Queue-Map/HG/$(basename "$i" .tar.gz)/$(basename "$j" .html)/node.html
        echo ""
    done
    rm $i # So we don't have anymore *gz's in the dir
done

