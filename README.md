Documentation location at: https://nick-fournier-rsg.github.io/pyosrm/


You must have an OSRM server running somewhere to use this package. You can run your own server or use a public one. The public ones are not recommended for production use.

To setup your own server, see the [OSRM documentation](https://github.com/Project-OSRM/osrm-backend). Below are instructions for setting up your own server and routing requests to the correct profile using nginx.

# Setup and Installation

There are three steps (or 2 if you use a pre-built docker image) to setting up the OSRM server:

1. Clone and compile the OSRM backend
2. Prepare the OSM data for OSRM
3. Run the server
4. (Optional) Route requests to the correct profile using nginx

I have provided a two sets of setup scripts in `.sh` bash files. One for locally compiling OSRM and another for running the Docker image, choose one.

The docker images are fast and easy to setup, but require a lot of disk space since each profile requires its own set of data.
The compiled version is more flexible and can share the same source data between profiles, but requires more setup.

#### Compiled
- build.sh
- prepare.sh
- run.sh
  
#### Docker
- docker_prepare.sh
- docker_run.sh

To make a script executable, run the following command:
```bash
chmod +x <script_name>.sh
```

## 1. Building the OSRM backend (not using Docker)

Skip this step if you are using the Docker image.

I have created a clone, build, and install bash script to automate the process. This script will clone the OSRM backend, build it, and install it. It will also install the dependencies required to build the OSRM backend. 

You may run it with the following commands:
```bash
sudo ./build.sh         # run the script
```

https://github.com/nick-fournier-rsg/pyrouting/blob/4dedb7ea87373ffe1e5f062af0e6391d9f5aa4ab/scripts/osrm/build.sh#L1-L22

## 2. Prepare OSRM data

The first step is to prepare the OSM data for use with OSRM. This is done with the OSRM backend commands:
- `osrm-extract`
- `osrm-partition`
- `osrm-customize`

OSRM is a high-performance routing engine that leverages a fair bit of pre-computing using defined mode "profiles" to make routing ultra fast. Default profiles are `car`, `bicycle`, and `foot`. You can also create custom profiles.

To run multiple profiles, you have to run separate OSRM servers with separately prepared OSRM files in separate directories. 

Edit the `osm_region` and `osm_area` variables to match the region and area you want in this helper script:

https://github.com/nick-fournier-rsg/pyrouting/blob/4dedb7ea87373ffe1e5f062af0e6391d9f5aa4ab/scripts/osrm/docker_prepare.sh#L1-L28

It will download the OSM file from [Geofabrik](https://download.geofabrik.de/) if it doesn't exist, then runs the osrm-extract, osrm-partition, and osrm-customize commands. It will place the extracted files into a separate directory named after the profile.

***Note that the extraction process requires A LOT of memory, something like 10x the pbf file size for bicycle profiles. Easiest solution is to add swap space to your machine. 


#### Compiled osrm-backend option

https://github.com/nick-fournier-rsg/pyrouting/blob/4dedb7ea87373ffe1e5f062af0e6391d9f5aa4ab/scripts/osrm/prepare.sh#L1-L38

## 3. Run servers

Once all the profiles have been prepared, an OSRM backend routing server can be started for each profile. e.g.,
```bash
sudo osrm-routed --port 5000:5000 --algorithm mld /path/to/profile.osrm
```

A seperate server must be started for each profile running on a different port. You can do this manually with `screen`, or in a one-liner you can send them to the background with '&'. The `docker_run.sh` script will start the servers for each profile.

https://github.com/nick-fournier-rsg/pyrouting/blob/4dedb7ea87373ffe1e5f062af0e6391d9f5aa4ab/scripts/osrm/docker_run.sh#L1-L5

#### Compiled osrm-backend option
https://github.com/nick-fournier-rsg/pyrouting/blob/4dedb7ea87373ffe1e5f062af0e6391d9f5aa4ab/scripts/osrm/run.sh#L1-L5


## 4. Nginx
To route requests to the correct profile, you can use a reverse proxy like nginx.

The following is an example of how to route requests to the correct profile using nginx. This is a simple example that routes requests based on the path.

First install nginx:
```bash
sudo apt-get update
sudo apt-get install nginx
sudo nano /etc/nginx/conf.d/osrm.conf
```

Then edit the nginx configuration file to route requests to the correct port based on the path. This example listens on port 80 and routes requests to the correct port based on the path.

```conf /etc/nginx/conf.d/osrm.conf
server {
        listen 80;
        listen [::]:80;
        server_name osrm.your-domain.com;

        # Logs
        access_log /var/log/nginx/osrm.access;
        error_log /var/log/nginx/osrm.error;

        location /route/v1/driving   { proxy_pass http://localhost:5000; }
        location /route/v1/walking   { proxy_pass http://localhost:5001; }
        location /route/v1/cycling   { proxy_pass http://localhost:5002; }

        # Everything else is a mistake and returns an error
        location / {
                add_header Content-Type text/plain;
                return 404 'Your request is bad and you should feel bad.';
        }
}

```

Then test and restart nginx if OK:
```bash
sudo nginx -t
sudo systemctl restart nginx
```

I haven't tested this yet but it should work? The nginx configuration is from the OSRM documentation:
https://github.com/Project-OSRM/osrm-backend/wiki/Running-OSRM#running-multiple-profiles-on-one-machine