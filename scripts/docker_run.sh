#!/bin/bash

docker run -t -i -p 5000:5000 -v "${PWD}/car:/data/car" ghcr.io/project-osrm/osrm-backend osrm-routed --algorithm mld /data/car/us-west-latest.osrm &
docker run -t -i -p 5001:5001 -v "${PWD}/bike:/data/bike" ghcr.io/project-osrm/osrm-backend osrm-routed --algorithm mld /data/bike/us-west-latest.osrm &
docker run -t -i -p 5002:5002 -v "${PWD}/foot:/data/foot" ghcr.io/project-osrm/osrm-backend osrm-routed --algorithm mld /data/foot/us-west-latest.osrm &