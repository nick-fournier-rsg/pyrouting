@REM This is for Windows

set osm_area="us-west-latest"

docker run -t -i -p 5000:5000 -v "%cd%/data/car:/data/car" ghcr.io/project-osrm/osrm-backend osrm-routed --algorithm mld /data/car/%osm_area%.osrm &
docker run -t -i -p 5001:5001 -v "%cd%/data/bicycle:/data/bike" ghcr.io/project-osrm/osrm-backend osrm-routed --algorithm mld /data/bicycle/%osm_area%.osrm &
docker run -t -i -p 5002:5002 -v "%cd%/data/foot:/data/foot" ghcr.io/project-osrm/osrm-backend osrm-routed --algorithm mld /data/foot/%osm_area%.osrm &