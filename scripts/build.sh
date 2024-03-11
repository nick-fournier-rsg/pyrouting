#!/bin/bash

# Install the dependencies
sudo apt-get update
sudo apt-get upgrade -y

# Optional: Install unattended-upgrades
# sudo apt-get install unattended-upgrades
# Add "APT::Periodic::Unattended-Upgrade "1"; to the file if not there

sudo apt-get install build-essential git cmake
sudo apt-get install libboost-all-dev libtbb-dev liblua5.2-dev libluabind-dev libstxxl-dev libxml2 libxml2-dev libosmpbf-dev libbz2-dev libprotobuf-dev


# Clone the osrm-backend repository
git clone https://github.com/Project-OSRM/osrm-backend.git
cd osrm-backend

# Build the osrm-backend
cd build
cmake ..
sudo make install