Documentation location at: https://nick-fournier-rsg.github.io/pyosrm/


For different profiles, you have to run separate OSRM servers with separately extracted OSM files in separate directories. Here is a helper script to download the OSM file if it doesn't exist, then runs the osrm-extract, osrm-partition, and osrm-customize commands. It will place the extracted files into a separate directory named after the profile. 

Edit the `osm_region` and `osm_area` variables to match the region and area you want to download from [Geofabrik](https://download.geofabrik.de/). Then run the script to download the OSM file and extract the profiles.

To execute the script, you have to make it executable:
```bash
chmod +x setup_script.sh
chmod +x run_servers.sh
```

https://github.com/nick-fournier-rsg/pyosrm/blob/cbf139c32ed005f7cf42c5a5e07c813202a29cbb/setup_script.sh#L1-L28

To run the servers simultaneously, you have to spin up separate instances with different ports. You can run them on the same machine you can send them to the background with '&'. So to run all three profiles, the commands would be:

https://github.com/nick-fournier-rsg/pyosrm/blob/cbf139c32ed005f7cf42c5a5e07c813202a29cbb/run_script.sh#L1-L5

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