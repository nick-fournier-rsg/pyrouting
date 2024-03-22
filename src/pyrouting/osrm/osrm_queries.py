"""
This module provides a Python interface to the Open Source Routing Machine (OSRM) API.
"""
from functools import wraps
import requests
import pandas as pd
from pyrouting.osrm import osrm_urls
from pyrouting.osrm import osrm_matching
from pyrouting.osrm import osrm_unpack


class OSRMQueries:
    """
    This class provides methods for constructing URLs for the OSRM API services.
    """
    def __init__(self, host: str = 'localhost', port: int = 5000):
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

    @wraps(osrm_urls.route_url)
    def route(self, *args, **kwargs) -> dict:
        """
        This function wraps the osrm_urls.route_url function and makes the HTTP request.

        Returns:
            dict: A JSON dictionary containing the full request response.
        """
        kwargs.update({'host': self.host, 'port': self.port})
        url = osrm_urls.route_url(*args, **kwargs)
        return requests.get(url, timeout=5).json()

    @wraps(osrm_urls.match_url)
    def match(self, *args, **kwargs) -> dict:
        """
        This function wraps the osrm_urls.match_url function and makes the HTTP request.

        Returns:
            dict: A JSON dictionary containing the full request response.
        """
        kwargs.update({'host': self.host, 'port': self.port})
        url = osrm_urls.match_url(*args, **kwargs)
        return requests.get(url, timeout=5).json()

    @wraps(osrm_urls.table_url)
    def table(self, *args, **kwargs) -> dict:
        """
        This function wraps the osrm_urls.table_url function and makes the HTTP request.

        Returns:
            dict: A JSON dictionary containing the full request response.
        """
        kwargs.update({'host': self.host, 'port': self.port})
        url = osrm_urls.table_url(*args, **kwargs)
        return requests.get(url, timeout=5).json()

    @wraps(osrm_matching.match_df)
    def match_df(self, *args, **kwargs) -> dict | pd.DataFrame:
        """
        This function wraps the osrm_matching.match_df function and returns a list of
        request responses.

        Returns:
            list: A list of JSON dictionaries containing the full request response.
        """

        # If kargs has "unpack", pop this out for unpacking after querying
        unpack = kwargs.pop('unpack')

        # Add the host and port to the kwargs
        kwargs.update({'host': self.host, 'port': self.port})
        response = osrm_matching.match_df(*args, **kwargs)

        if isinstance(unpack, list) and len(unpack) > 0:
            result = [osrm_unpack.unpack_match(r, unpack) for r in response.values()]
            matches_df = pd.DataFrame(result, columns=unpack, index=list(response.keys()))

            # Concatenate the results with the original DataFrame
            df = args[0] if isinstance(args[0], pd.DataFrame) else kwargs.get('df')
            return pd.concat([df, matches_df], axis=1)

        return response
