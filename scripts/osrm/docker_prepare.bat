@REM This is for Windows

set osm_region="north-america"
set osm_area="us-west-latest"

@REM Loop through the profiles
for /F %profile% in ("car" "bicycle" "foot") do (
    mkdir -p data/%profile%

    @REM Copy the OSM file to the profile folder
    cp data/%osm_area%.osm.pbf data/%profile%/%osm_area%.osm.pbf

    @REM Run the osrm-backend
    docker run -t -v "%cd%/data/%profile%:/data/%profile%" ghcr.io/project-osrm/osrm-backend osrm-extract -p /opt/%profile%.lua /data/%profile%/%osm_area%.osm.pbf || echo "osrm-extract failed"
    docker run -t -v "%cd%/data/%profile%:/data/%profile%" ghcr.io/project-osrm/osrm-backend osrm-partition /data/%profile%/%osm_area%.osrm || echo "osrm-partition failed"
    docker run -t -v "%cd%/data/%profile%:/data/%profile%" ghcr.io/project-osrm/osrm-backend osrm-customize /data/%profile%/%osm_area%.osrm || echo "osrm-customize failed"
)