Documentation location at: https://nick-fournier-rsg.github.io/pyosrm/


For different profiles, you have to run separate OSRM servers with separately extracted OSM files in separate directories. Here is a possible helper script to download the OSM file if it doesn't exist, then runs the osrm-extract, osrm-partition, and osrm-customize commands. It will place the extracted files into a separate directory named after the profile. 


To create the script, run the following commands:
```bash
touch setup_script.sh
touch run_servers.sh
chmod +x setup_script.sh
chmod +x run_servers.sh
```

Which will create a file called `setup_script.sh`. Copy and paste this content into the file and edit the `osm_region` and `osm_area` variables to match the region and area you want to download. Then run the script to download the OSM file and extract the profiles.

```bash ./setup_script.sh
#!/bin/bash

osm_region="north-america"
osm_area="us-west-latest"
fpath="./${profile}/${osm_area}.osm.pbf"

for profile in "car" "bike" "foot"
do
    mkdir -p ${profile}

    if [ -e ${fpath} ]
    then
            echo "${fpath} already exists. Skipping download"
    else
            echo "Downloading OSM file to ${fpath}"
            wget https://download.geofabrik.de/${osm_region}/${osm_area} -P ./data
    fi
    cp ./data/${osm_area}.osm.pbf ./${profile}/${osm_area}.osm.pbf
    docker run -t -v "${PWD}/${profile}:/data/${profile}" ghcr.io/project-osrm/osrm-backend osrm-extract -p /opt/${profile}.lua /data/${profile}/${osm_area}.osm.pbf || echo "osrm-extract failed"
    docker run -t -v "${PWD}/${profile}:/data/${profile}" ghcr.io/project-osrm/osrm-backend osrm-partition /data/${profile}/${osm_area}.osrm || echo "osrm-partition failed"
    docker run -t -v "${PWD}/${profile}:/data/${profile}" ghcr.io/project-osrm/osrm-backend osrm-customize /data/${profile}/${osm_area}.osrm || echo "osrm-customize failed"

done
```

To run the servers simultaneously, you have to spin up separate instances with different ports. You can run them on the same machine you can send them to the background with '&'. So to run all three profiles, the commands would be:

```bash ./run_servers.sh
docker run -t -i -p 5000:5000 -v "${PWD}/car:/data/car" ghcr.io/project-osrm/osrm-backend osrm-routed --algorithm mld /data/car/us-west-latest.osrm &
docker run -t -i -p 5001:5001 -v "${PWD}/bike:/data/bike" ghcr.io/project-osrm/osrm-backend osrm-routed --algorithm mld /data/bike/us-west-latest.osrm &
docker run -t -i -p 5002:5002 -v "${PWD}/foot:/data/foot" ghcr.io/project-osrm/osrm-backend osrm-routed --algorithm mld /data/foot/us-west-latest.osrm &
```

Alternatively you could use the `screen` command to run the servers in separate screens manually. From there a proxy can be used to route requests to the correct port based on the profile.
```conf nginx.conf
    server {
            listen 80 default_server;
            listen [::]:80 default_server ipv6only=on;

            # catch all v5 routes and send them to OSRM
            location /route/v1/driving   { proxy_pass http://localhost:5000; }
            location /route/v1/walking   { proxy_pass http://localhost:5001; }
            location /route/v1/cycling   { proxy_pass http://localhost:5002; }

            # Everything else is a mistake and returns an error
            location /           {
            add_header Content-Type text/plain;
            return 404 'Your request is bad and you should feel bad.';
            }
    }
```

I haven't tested this yet but it should work? The nginx configuration is from the OSRM documentation:
https://github.com/Project-OSRM/osrm-backend/wiki/Running-OSRM#running-multiple-profiles-on-one-machine