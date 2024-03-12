#!/bin/bash

osm_region="north-america"
osm_area="us-west-latest"

cd ~/osrm
mkdir -p data

if [ -e "data/${osm_area}.osm.pbf" ]
then
        echo "~/osrm/data/${osm_area}.osm.pbf already exists. Skipping download"
else
        echo "Downloading OSM file to ./data/${osm_area}.osm.pbf"
        wget https://download.geofabrik.de/${osm_region}/${osm_area}.osm.pbf -P ./data
fi

for profile in "car" "bicycle" "foot"
do
    
    # Check if the profile exists
    if [ -e "data/${profile}" ]
    then    
        mkdir -p data/${profile}

        # Rather than copy the large file, just make a symbolic link for osrm to extract into a new folder.
        ln -s data/${osm_area}.osm.pbf data/${profile}/${osm_area}.osm.pbf

        osrm-extract ~data/${profile}/${osm_area}.osm.pbf -p ~/osrm-backend/profiles/${profile}.lua
        # Contraction Hierarchies. Faster but does not allow for traffic updates
        # osrm-contract ${osm_area}.osrm    
        osrm-partition ~/data/${profile}/${osm_area}.osrm
        osrm-customize ~/data/${profile}/${osm_area}.osrm
      
    else
        echo "data/${profile} already exists. Skipping profile"
    fi

done