"""
This module contains higher order functions for processing dataframes of trip data in bulk.
"""
import pandas as pd
import numpy as np
import requests
from .query import URLQueries
from .concurrency import ConcurrentRequests


class BulkQueries(URLQueries):
    """
    This class provides higher order functions for processing dataframes of trip data in bulk.
    """
    host = 'localhost'
    port = 5000

    def match_df(
        self,
        df: pd.DataFrame,
        mode: str,
        renames: dict[str, str] | None = None,
        group_col: str | None = None,
        geometries: str = 'polyline',
        annotations: str = 'duration',
        gaps: bool = False,
        tidy: bool = False,
        steps: bool = False,
        dt_format: str = '%Y-%m-%d %H:%M:%S%z'
    ) -> dict:
        """

        Map match trip locations points to osrm route from dataframes.

        It then makes parallel map matching requests to the OSRM server and
        returns the matched trip points.

        Args:
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
            gaps (bool, optional): Allows the input track modification to obtain a better match
                for noisy traces.
            steps (bool, optional): Return route steps for each route leg.
            waypoints (list, optional): Selected input coordinates as waypoints.
            dt_format (str, optional): The format of the timestamps if not integer seconds.
                Default is '%Y-%m-%d %H:%M:%S%z'.

        Returns:
            json dict: A JSON dictionary containing the matched coordinates and metadata.
        """

        assert isinstance(df, pd.DataFrame), 'locations_df must be a pandas DataFrame'

        # Assert mode is either drive, bicycle, or foot
        assert mode in ['driving', 'bicycle', 'foot'], \
            'mode must be "driving", "bicycle", or "foot".'

        # Rename the columns
        df.rename(columns=renames, inplace=True)

        # Assert required columns are present
        for col in ['lat', 'lon']:
            assert col in df.columns, f'{col} not present in locations_df'

        # If timestamp is a string, convert to integer seconds since UNIX epoch
        if 'timestamp' in df.columns and df['timestamp'].dtype != 'int64':
            df['timestamp'] = pd.to_datetime(df['timestamp'], format=dt_format).astype('int64')
            df['timestamp'] //= 10**9

        # Extract the columns as numpy arrays
        if group_col:
            # Sort by group_col and timestamp
            df = df.sort_values(by=[group_col, 'timestamp']).set_index(group_col)

            # Map match each group
            indexmap = np.unique(df.index, return_index=True)

            # Split the dataframe by group_col
            latlons = np.split(df[['lat', 'lon']].values, indexmap[1])
            timestamps = [None]*indexmap[1].size
            radiuses = [None]*indexmap[1].size
            waypoints = [None]*indexmap[1].size

            if 'timestamp' in df.columns:
                timestamps = np.split(df.timestamp.to_numpy(), indexmap[1])

            if 'radius' in df.columns:
                radiuses = np.split(df.radius.to_numpy(), indexmap[1])

            if 'waypoint' in df.columns:
                waypoints = np.split(df.waypoint.to_numpy(), indexmap[1])

            # Zip up the arrays
            split_data = list(zip(latlons, timestamps, radiuses, waypoints))[1:]

            # Construct a list of urls
            def generate_urls(data):
                kwargs = {
                    'host': self.host,
                    'port': self.port,
                    'mode': mode,
                    'geometries': geometries,
                    'annotations': annotations,
                    'gaps': gaps,
                    'tidy': tidy,
                    'steps': steps,
                    'dt_format': dt_format,
                    'coordinates': data[0],
                    'timestamps': data[1],
                    'radiuses': data[2],
                    'waypoints': data[3]
                }
                return self.match_url(**kwargs)

            urls = [generate_urls(data) for data in split_data]

            # Make concurrent requests
            concurrency = ConcurrentRequests()
            results = concurrency.get(urls)

        else:
            # Map match the entire dataframe in single request
            kwargs = {
                'coordinates': df[['lat', 'lon']].values,
                'timestamps': df.timestamp.to_numpy(),
                'host': self.host,
                'port': self.port,
                'mode': mode,
                'geometries': geometries,
                'annotations': annotations,
                'radiuses': df.radius.to_numpy(),
                'gaps': gaps,
                'tidy': tidy,
                'steps': steps,
                'waypoints': df.waypoint.to_numpy(),
                'dt_format': dt_format
            }
            url = self.match_url(**kwargs)
            results = requests.get(url, timeout=5).json()

        assert isinstance(results, dict), 'results must be a dictionary'

        return results


if __name__ == '__main__':
    LOC_PATH = (
        'C:/Users/nick.fournier/OneDrive - Resource Systems Group, Inc/Desktop/'
        'sample_locations.csv'
    )
    locations = pd.read_csv(LOC_PATH)

    bulky = BulkQueries()
    bulky.host = '192.168.1.126'
    bulky.port = 5000

    bulky.match_df(
        locations, mode='drive', group_col='trip_id', renames={'collect_time': 'timestamp'}
    )
