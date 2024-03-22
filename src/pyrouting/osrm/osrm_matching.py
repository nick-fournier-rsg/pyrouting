"""
This module contains the bulk dataframe-based map matching function for the OSRM API.
"""
from typing import Iterator
import numpy as np
import pandas as pd
import requests
from pyrouting.osrm import osrm_urls
from pyrouting.utils import ConcurrentRequests


# Construct a list of urls
def _build_url(*args, **kwargs) -> str:
    """
    This is a helper function to generate a list of URLs for the OSRM API.

    Returns:
        str: A string containing the URL.
    """
    # Append kwargs with data
    url_kwargs = {
        **kwargs,
        **{
            'coordinates': args[0],
            'timestamps': args[1],
            'radiuses': args[2],
            'waypoints': args[3]
        }
    }
    return osrm_urls.match_url(**url_kwargs)


def _url_generator(iterable, std_kwargs: dict) -> Iterator:
    for item in iterable:
        url_kwargs = {
            **std_kwargs,
            **{
                'coordinates': item[0],
                'timestamps': item[1],
                'radiuses': item[2],
                'waypoints': item[3]
            }
        }
        yield osrm_urls.match_url(**url_kwargs)


def build_urls(
    df: pd.DataFrame,
    group_col: str | None, **kwargs
) -> tuple[None | np.ndarray, list | Iterator]:
    """
    This function constructs a list of URLs for the OSRM API based on the input dataframe.

    Args:
        df (pd.DataFrame): A dataframe of trip data. Must contain columns:
            lat, lon, with optional timestamp, waypoint, and radius.
        group_col (str | None): The column name to group the dataframe by.

    Returns:
        list: A list of URLs for the OSRM API.
    """

    # If no group_col, build a single URL for the entire dataframe
    if group_col is None:
        # Build a single URL for the entire dataframe
        args = [
            df[['lat', 'lon']].values,
            df.timestamp.to_numpy(),
            df.radius.to_numpy(),
            df.waypoint.to_numpy()
            ]
        urls = _build_url(args, kwargs)

        return None, [urls]

    # Sort by group_col and timestamp
    df = df.sort_values(by=[group_col, 'timestamp']).set_index(group_col)

    # Map match each group
    indexmap = np.unique(df.index, return_index=True)

    # data is arg array [latlons, timestamps, radiuses, waypoints]
    data = []

    # Split the dataframe by group_col
    data.append(np.split(df[['lat', 'lon']].values, indexmap[1], axis=0)[1:])

    # If these optional columns are present, split them as well, else use dummy
    dummy = [None]*indexmap[1].size
    for col in ['timestamp', 'radius', 'waypoint']:
        if col in df.columns:
            data.append(np.split(df[col].to_numpy(), indexmap[1], axis=0)[1:])
        else:
            data.append(dummy)

    # Construct the URLs
    url_genny = _url_generator(zip(*data), kwargs)

    # Return the indexmap and urls
    return indexmap[0], url_genny


def match_df(
    df: pd.DataFrame,
    renames: dict[str, str] | None = None,
    group_col: str | None = None,
    **kwargs
) -> dict:
    """

    Map match trip locations points to osrm route from dataframes.

    It then makes parallel map matching requests to the OSRM server and
    returns the matched trip points.

    Args:
        host (str, optional): The host URL. Defaults to 'localhost:5000'.
        port (int, optional): The port number. Defaults to 5000.
        df (pd.DataFrame): A dataframe of trip data. Must contain columns:
            lat, lon, with optional timestamp, waypoint, and radius.
        mode (str, optional): The mode of transportation. One of driving, walking, cycling.
        group_col (str, optional): The column name to group the dataframe by.
        renames (dict, optional): A dictionary of column renames for lat, lon, and timestamp.
        coordinates (list): A list of coordinates in the form [(lon1, lat1), (lon2, lat2), ...].
        mode (str, optional): The mode of transportation. One of driving, walking, cycling.
        geometries (str, optional): Returned route geometry format as polyline,
            polyline6, geojson. Default is polyline.
        annotations (str, optional): Returns additional metadata for each coordinate along the
            route geometry. One of true, false, nodes, distance, duration, datasources, weight,
            speed.
        radiuses (list, optional): Search radius in meters for each coordinate.
        gaps (str, optional): Either 'split' or 'ignore' (default). Allows the input track
            modification to obtain a better match for noisy traces.
        steps (bool, optional): Return route steps for each route leg.
        waypoints (list, optional): Selected input coordinates as waypoints.
        dt_format (str, optional): The format of the timestamps if not integer seconds.
            Default is '%Y-%m-%d %H:%M:%S%z'.

    Returns:
        json list: A JSON list of dictionaries containing the matched coordinates and metadata.
    """

    # Set default kwargs
    defaults = {
        # 'host': 'localhost',
        # 'port': 5000,
        'mode': 'driving',
        'geometries': 'polyline',
        'annotations': 'true',
        'radiuses': None,
        'waypoints': None,
        'gaps': 'ignore',
        'tidy': None,
        'steps': None,
        'dt_format': '%Y-%m-%d %H:%M:%S%z'
    }

    # Assert host and port exist
    assert 'host' in kwargs, 'Missing host in kwargs specified in match_df'
    assert 'port' in kwargs, 'Missing port in kwargs specified in match_df'

    for key, value in defaults.items():
        kwargs.setdefault(key, value)

    assert isinstance(df, pd.DataFrame), 'locations_df must be a pandas DataFrame'

    # Assert mode is either drive, bicycle, or foot
    assert kwargs['mode'] in ['driving', 'bicycle', 'foot'], \
        'mode must be "driving", "bicycle", or "foot".'

    # Rename the columns
    df = df.rename(columns=renames)

    # Assert required columns are present
    for col in ['lat', 'lon']:
        assert col in df.columns, f'{col} not present in locations_df'

    # If timestamp is a string, convert to integer seconds since UNIX epoch
    if 'timestamp' in df.columns and df['timestamp'].dtype != 'int64':
        df['timestamp'] = pd.to_datetime(
            df['timestamp'],
            format=kwargs['dt_format']
        ).astype('int64')
        df['timestamp'] //= 10**9

    idx, urls = build_urls(df, group_col, **kwargs)

    # If only one URL, make a single request
    if not group_col and df[group_col].nunique() == 1:
        assert isinstance(urls, list), 'urls must be a list of strings'
        return requests.get(urls[0], timeout=5).json()

    # If multiple URLs, use concurrent requests
    concurrency = ConcurrentRequests()
    results = concurrency.get(urls)

    assert idx is not None, 'idx must be an iterable'
    return dict(zip(idx, results))
