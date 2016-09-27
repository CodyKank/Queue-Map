#!/bin/bash

#Bash script to gather the html files for a Queuemap webpage. It will grab the files from a web-hosted service,
#like the www directory in my Public afs space.

#local info:
pswd="LOCAL PASSWORD HERE!! OR CHANGE SUDOERS FILE!!!" #or configure sudoers file

desired_path="/var/www/html" #typicaly /var/www/html  (you don't need the last '/')

curl_url="CURL URL HERE!!!!!!!!!!!!!!!!!" #Don't need last '/'
#Gathering files from CRCFE using curl

curl -o index-long.html $curl_url/index-long.html

curl -o long_mem.html $curl_url/long_mem.html

curl -o index-debug.html $curl_url/index-debug.html

curl -o debug_mem.html $curl_url/debug_mem.html

curl -o pending_content.html $curl_url/pending.html

curl -o sub-debug.tar.gz $curl_url/sub-debug.tar.gz

curl -o sub-long.tar.gz $curl_url/sub-long.tar.gz

#Moving the files once on the web-server to proper locations

echo $pswd | sudo -S mv index-long.html $desired_path/Long/index-long.html

echo $pswd | sudo -S mv long_mem.html $desired_path/Long-memory/index-long.html

echo $pswd | sudo -S mv index-debug.html $desired_path/Debug/index-debug.html

echo $pswd | sudo -S mv debug_mem.html $desired_path/Debug-memory/index-debug.html

echo $pswd | sudo -S mv pending_content.html $desired_path/Pending/pending_content.html

#Setting up node files:

tar -xzf sub-debug.tar.gz
for i in debug@*;
do
        echo $pswd | sudo -S mv $i $desired_path/Debug/$i/sub-index.html
done

tar -xzf sub-long.tar.gz
for j in d6copt*;
do
        echo $pswd | sudo -S mv $j $desired_path/Long/$j/sub-index.html
done
