#!/bin/bash

#Bash script to gather the html files for a Queuemap webpage. It will grab the files from a web-hosted service,
#like the www directory in my Public afs space.

#local info:
pswd="LOCAL(SERVER) PASSWORD HERE!!!" #or configure sudoers file

desired_path="DESIRED PATH FOR SERVER HERE!" #typicaly /var/www/html  (you don't need the last '/')

curl_url="URL FOR CURL GOES HERE" #Don't need last '/'
#Gathering files from CRCFE using wget

curl -o index-long.html $curl_url/index-long.html

curl -o index-debug.html $curl_url/index-debug.html

curl -o pending_content.html $curl_url/pending.html

curl -o sub-debug.tar.gz $curl_url/sub-debug.tar.gz

curl -o sub-long.tar.gz $curl_url/sub-long.tar.gz

#Moving the files once on the web-server to proper locations

echo $pswd | sudo -S mv index-long.html $desired_path/Long/index-long.html

echo $pswd | sudo -S mv index-debug.html $desired_path/Debug/index-debug.html

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
