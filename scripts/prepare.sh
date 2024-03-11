#!/bin/bash

osm_region="north-america"
osm_area="us-west-latest"

if [ -e "./data/${osm_area}.osm.pbf" ]
then
        echo "./data/${osm_area}.osm.pbf already exists. Skipping download"
else
        echo "Downloading OSM file to ./data/${osm_area}.osm.pbf"
        wget https://download.geofabrik.de/${osm_region}/${osm_area}.osm.pbf -P ./data
fi

for profile in "car" "bicycle" "foot"
do
    mkdir -p ${profile}

    # Rather than copy the large file, just make a symbolic link for osrm to extract into a new folder.
    ln -s ~osrm/data/${osm_area}.osm.pbf ~/osrm/${profile}/${osm_area}.osm.pbf

    osrm-extract ~/osrm/${profile}/${osm_area}.osm.pbf -p ~/osrm-backend/profiles/${profile}.lua
    # Contraction Hierarchies. Faster but does not allow for traffic updates
    # osrm-contract ${osm_area}.osrm    
    osrm-partition ~/osrm/${profile}/${osm_area}.osrm
    osrm-customize ~/osrm/${profile}/${osm_area}.osrm

done