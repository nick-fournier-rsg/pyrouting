"""
This module provides a Python interface to the Open Source Routing Machine (OSRM) API.
"""
import requests
from pyosrm import utils


class PyOSRM:
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

    def table(self,
              coordinates: list[tuple],
              mode: str = 'driving',
              annotations: str = 'duration',
              sources: list[int] | None = None,
              destinations: list[int] | None = None
              ) -> dict:
        """
        Calculate the duration of the fastest route between all pairs of the supplied coordinates.

        Args:
            coordinates (list): A list of coordinates in the form [(lon1, lat1), (lon2, lat2), ...].
            sources (list, optional): Use location with given index as source.
            destinations (list, optional): Use location with given index as destination.

        Returns:
            _type_: _description_
        """

        assert mode in ['driving', 'walking', 'cycling'], \
            'mode must be one of "driving", "walking", or "cycling"'

        # Annotations must be either duration, distance, or duration and distance
        assert annotations in ['duration', 'distance'], \
            'annotations must be one of "duration", "distance"'

        # Construct the URL
        url = f'{self.host}:{self.port}/table/v1/{mode}/'
        url += ';'.join([f'{c[1]},{c[0]}' for c in coordinates])

        # Create empty options list
        options = []
        if isinstance(sources, list):
            sources_str = ';'.join([str(s) for s in sources])  # type: ignore
            options.append(f'sources={sources_str}')

        if isinstance(sources, list):
            destinations_str = ';'.join([str(d) for d in destinations])  # type: ignore
            options.append(f'&destinations={destinations_str}')

        if isinstance(annotations, list):
            options.append(f'annotations={annotations}')

        # Concatenate the options strings with & in between
        if len(options) > 0:
            options_str = '&'.join(options)
            url += f'?{options_str}'

        response = requests.get(url, timeout=10)
        return response.json()

    def match(self,
              coordinates: list[tuple],
              mode: str = 'driving',
              timestamps: list[int] | list[str] | None = None,
              geometries: str = 'polyline',
              annotations: str = 'false',
              radiuses: list[int] | None = None,
              gaps: bool = False,
              steps: bool = False,
              waypoints: list[int] | None = None,
              dt_format: str = '%Y-%m-%d %H:%M:%S%z'
              ):
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
            waypoints (list, optional): Selected input coordinates as waypoints.
            dt_format (str, optional): The format of the timestamps if not integer seconds.
                Default is '%Y-%m-%d %H:%M:%S%z'.

        Returns:
            json dict: A JSON dictionary containing the matched coordinates and metadata.
        """

        assert mode in ['driving', 'walking', 'cycling'], \
            'mode must be one of "driving", "walking", or "cycling"'

        url = f'{self.host}:{self.port}/match/v1/{mode}/'
        url += ';'.join([f'{c[1]},{c[0]}' for c in coordinates])

        # Create empty options list
        options = []
        if isinstance(timestamps, list):
            # If timestamp is a string, convert to a list of integers
            timestamps = [utils.parse_datetime_to_int(t, dt_format) for t in timestamps]
            timestamps_str = ';'.join([str(t) for t in timestamps])  # type: ignore
            options.append(f'timestamps={timestamps_str}')

        if isinstance(radiuses, list):
            radiuses_str = ';'.join([str(r) for r in radiuses])  # type: ignore
            options.append(f'radiuses={radiuses_str}')

        if isinstance(waypoints, list):
            waypoints_str = ';'.join([str(w) for w in waypoints])  # type: ignore
            options.append(f'waypoints={waypoints_str}')

        # Add the options to the URL
        # for opt in ['steps', 'gaps', 'annotations', 'geometries']:
        #     if locals()[opt]:
        #         options.append(f'{opt}={locals()[opt]}')

        if steps:
            options.append('steps=true')

        if gaps:
            options.append('gaps=true')

        if annotations:
            options.append(f'annotations={annotations}')

        if geometries:
            options.append(f'geometries={geometries}')

        # Concatenate the options strings with & in between
        if len(options) > 0:
            options_str = '&'.join(options)
            url += f'?{options_str}'

        response = requests.get(url, timeout=10)
        return response.json()

    def route(self,
              coordinates: list[tuple],
              mode: str = 'driving',
              geometries: str = 'polyline',
              steps: bool = False,
              alternatives: int = 1,
              annotations: str = 'false',
              continue_straight: bool = False,
              waypoints: list[int] | None = None
              ) -> dict:
        """
        This function returns the fastest route between the supplied coordinates.

        Args:
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
            json dict: A JSON dictionary containing the route and metadata.
        """

        url = f'{self.host}:{self.port}/route/v1/{mode}/'
        url += ';'.join([f'{c[1]},{c[0]}' for c in coordinates])

        # Create empty options list
        options = []

        if isinstance(waypoints, list):
            waypoints_str = ';'.join([str(w) for w in waypoints])  # type: ignore
            options.append(f'waypoints={waypoints_str}')

        # for opt in ['steps', 'alternatives', 'continue_straight', 'annotations', 'geometries']:
        #     if locals()[opt]:
        #         options.append(f'{opt}={locals()[opt]}')

        if steps:
            options.append('steps=true')

        if alternatives:
            options.append(f'alternatives={alternatives}')

        if continue_straight:
            options.append(f'continue_straight={continue_straight}')

        if annotations:
            options.append(f'annotations={annotations}')

        if geometries:
            options.append(f'geometries={geometries}')

        # Concatenate the options strings with & in between
        if len(options) > 0:
            options_str = '&'.join(options)
            url += f'?{options_str}'

        response = requests.get(url, timeout=10)
        return response.json()

    # def nearest(self, coordinates, number=1):
    #     url = self.host + '/nearest/v1/driving/'
    #     url += f'{coordinates[1]},{coordinates[0]}'
    #     url += f'?number={number}'
    #     response = requests.get(url, timeout=10)
    #     return response.json()

    # def trip(self, coordinates, steps=False, source=None, destination=None):
    #     url = self.host + '/trip/v1/driving/'
    #     url += ';'.join([f'{c[1]},{c[0]}' for c in coordinates])
    #     if source is not None:
    #         url += f'?source={source}'
    #     if destination is not None:
    #         url += f'&destination={destination}'
    #     if steps:
    #         url += '?steps=true'
    #     response = requests.get(url, timeout=10)
    #     return response.json()

    # def tile(self, z, x, y):
    #     url = self.host + f'/tile/v1/driving/{z}/{x}/{y}.mvt'
    #     response = requests.get(url, timeout=10)
    #     return response.content

    # def trip_to_df(self, trip):
    #     trip_points = []
    #     for leg in trip['trips'][0]['legs']:
    #         for step in leg['steps']:
    #             for intersection in step['intersections']:
    #                 trip_points.append(intersection['location'])
