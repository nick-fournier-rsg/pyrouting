"""
This module provides a Python interface to the Open Source Routing Machine (OSRM) API.
"""

import requests
from .bulk import BulkQueries


class PyOSRM(BulkQueries):
    """
    This class provides a Python interface to the Open Source Routing Machine (OSRM) API.
    """
    def __init__(self, host: str = 'localhost:5000', port: int = 5000):
        """
        Initialize the PyOSRM object.

        Args:
            host (str, optional): The host URL. Defaults to 'localhost:5000'.
        """

        # If does not start with https:// or http://, then add http://
        if not host.startswith('https://') and not host.startswith('http://'):
            host = 'http://' + host

        self.host = host
        self.port = port

    def testhost(self) -> bool:
        """
        Test the host URL.

        Returns:
            bool: True if the host is reachable, False otherwise.
        """

        # Test the host URL
        url = f'{self.host}:{self.port}'
        try:
            requests.head(url, timeout=5)
            return True
        except requests.exceptions.ConnectionError:
            return False

    def route(self, *args, **kwargs) -> dict:
        """
        Calculate the duration of the fastest route between all pairs of the supplied coordinates.

        Args:
            coordinates (list): A list of coordinates in the form [(lon1, lat1), (lon2, lat2), ...].
            mode (str, optional): The mode of transportation. One of driving, walking, cycling.
            annotations (str, optional): Returns additional metadata for each coordinate along the
                route geometry. One of true, false, nodes, distance, duration, datasources, weight,
                speed.
            sources (list, optional): Use location with given index as source.
            destinations (list, optional): Use location with given index as destination.

        Returns:
            dict: A JSON dictionary containing the route geometry and metadata.
        """
        kwargs.update({'host': self.host, 'port': self.port})
        url = super().route_url(*args, **kwargs)
        return requests.get(url, timeout=5).json()

    def match(self, *args, **kwargs) -> dict:
        """
        This function matches supplied coordinates to the road network and returns
        the nearest road segment for each point.

        Args:
            coordinates (list): A list of coordinates in the form [(lon1, lat1), (lon2, lat2), ...].
            mode (str, optional): The mode of transportation. One of driving, walking, cycling.
            timestamps (list, optional): A list of timestamps in seconds since UNIX epoch for
                each coordinate in the form [t1, t2, ...].
            geometries (str, optional): Returned route geometry format as polyline,
                polyline6, geojson. Default is polyline.
            annotations (str, optional): Returns additional metadata for each coordinate along the
                route geometry. One of true, false, nodes, distance, duration, datasources, weight,
                speed.
            radiuses (list, optional): Search radius in meters for each coordinate.
            gaps (bool, optional): Allows the input track modification to obtain a better match
                for noisy traces.
            steps (bool, optional): Return route steps for each route leg.
            waypoints (list, optional): Selected input coordinates as waypoints.
            dt_format (str, optional): The format of the timestamps if not integer seconds.
                Default is '%Y-%m-%d %H:%M:%S%z'.

        Returns:
            dict: A JSON dictionary containing the matched coordinates and metadata.
        """
        kwargs.update({'host': self.host, 'port': self.port})
        url = super().match_url(*args, **kwargs)
        return requests.get(url, timeout=5).json()

    def table(self, *args, **kwargs) -> dict:
        """
        This function returns the fastest route between the supplied coordinates.

        Args:
            mode (str, optional): The mode of transportation. One of driving, walking, cycling.
            coordinates (list): A list of coordinates in the form [(lon1, lat1), (lon2, lat2), ...].
            geometries (str, optional): Returned route geometry format as polyline,
                polyline6, geojson. Default is polyline.
            steps (bool, optional): Return route steps for each route leg.
            alternatives (int, optional): Search for N alternative routes. Default is 1.
            annotations (str, optional): Returns additional metadata for each coordinate along the
                route geometry. One of true, false, nodes, distance, duration, datasources, weight,
                speed.
            continue_straight (bool, optional): Forces the route to keep going straight at waypoints
                restricting u-turns. Default is false.
            waypoints (list, optional): Selected input coordinates as waypoints.

        Returns:
            dict: A JSON dictionary containing the route geometry and metadata.
        """
        kwargs.update({'host': self.host, 'port': self.port})
        url = super().table_url(*args, **kwargs)
        return requests.get(url, timeout=5).json()
