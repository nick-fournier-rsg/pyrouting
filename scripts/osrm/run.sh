#!/bin/bash

osrm-routed --port 5000 --algorithm mld ~/osrm/data/car/us-west-latest.osrm &
osrm-routed --port 5001 --algorithm mld ~/osrm/data/foot/us-west-latest.osrm &
osrm-routed --port 5002 --algorithm mld ~/osrm/data/bicycle/us-west-latest.osrm &
