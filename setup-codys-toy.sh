#!/bin/bash

#Script to set up the CRC Queue heat-map. Thats what it's called I guess.
#8/3/16
#Requires sudo permission. This script assumes you have apache2 running and 
#php7.0(or something compatible). Default path is listed below.

desired_path="/var/www/html" #you can change this if need be

sudo mkdir $desired_path/Debug
sudo mkdir $desired_path/Long

sudo mkdir $desired_path/Debug/templates
sudo mkdir $desired_path/Long/templates

