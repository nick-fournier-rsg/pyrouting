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
    cd ~/osrm

    # Copy the OSM file to the profile folder
    cp data/${osm_area}.osm.pbf ${profile}/${osm_area}.osm.pbf

    # Run the osrm-backend
    docker run -t -v "${PWD}/${profile}:/data/${profile}" ghcr.io/project-osrm/osrm-backend osrm-extract -p /opt/${profile}.lua /data/${profile}/${osm_area}.osm.pbf || echo "osrm-extract failed"
    docker run -t -v "${PWD}/${profile}:/data/${profile}" ghcr.io/project-osrm/osrm-backend osrm-partition /data/${profile}/${osm_area}.osrm || echo "osrm-partition failed"
    docker run -t -v "${PWD}/${profile}:/data/${profile}" ghcr.io/project-osrm/osrm-backend osrm-customize /data/${profile}/${osm_area}.osrm || echo "osrm-customize failed"

done