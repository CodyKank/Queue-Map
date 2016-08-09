#!/bin/bash

#CRC info;
pword="CRC-PASSWORD GOES HERE!!!!"
usename="CRC-USERNAME GOES HERE!!!"
dest="crcfe01.crc.nd.edu" #You can change this to which-ever front end you want
afs_path="PATH TO DIR OF PYTHON DAEMON" #(don't need last '/')

#local info:
pswd="LOCAL(SERVER) PASSWORD HERE!!!"

desired_path="DESIRED PATH FOR SERVER HERE!" #typicaly /var/www/html  (you don't need the last '/')

#Gathering files from CRCFE

sshpass -p "$pword" scp $usename@$dest:$afs_path/index-long.html $(pwd)/index-long.html

sshpass -p "$pword" scp $usename@$dest:$afs_path/index-debug.html $(pwd)/index-debug.html

sshpass -p "$pword" scp $usename@$dest:$afs_path/sub-debug.tar.gz $(pwd)/sub-debug.tar.gz

sshpass -p "$pword" scp $usename@$dest:$afs_path/sub-long.tar.gz $(pwd)/sub-long.tar.gz

#Moving the files once on the web-server to proper locations

echo $pswd | sudo -S mv index-long.html $desired_path/Long/index-long.html

echo $pswd | sudo -S mv index-debug.html $desired_path/Debug/index-debug.html

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
