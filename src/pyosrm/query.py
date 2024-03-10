"""
This module provides a Python interface to the Open Source Routing Machine (OSRM) API.
"""
from pyosrm.utils import parse_datetime_to_int


class URLQueries:
    """
    This class provides methods for constructing URLs for the OSRM API services.
    """

    @staticmethod
    def url_constructor(
        host: str,
        port: int,
        mode: str,
        coordinates: list[tuple],
        list_args: dict[str, list],
        option_args: dict[str, str],
    ) -> str:
        """
        Construct a URL string from a list of arguments and a dictionary of optional arguments.

        Args:
            list_args (dict[str, list]): A dictionary of list arguments.
            opt_args (dict[str, str]): A dictionary of single value options.

        Returns:
            str: A URL string.
        """

        # Combine the list_args and option_args
        kwargs = {**list_args, **option_args}

        # Construct the URL
        url = f'{host}:{port}/table/v1/{mode}/'
        url += ';'.join([f'{c[1]},{c[0]}' for c in coordinates])

        # Create empty options list
        options: list[str] = []

        # Stringify the kwargs
        for k, v in kwargs.items():
            if not v:
                continue

            if isinstance(v, list):
                _str = ';'.join([str(i) for i in v])

            elif isinstance(v, str | int | float | bool):
                _str = str(v).lower()

            else:
                raise ValueError('list_args must contain lists or strings')

            options.append(f'{k}={_str}')

        # Concatenate the options strings with & in between
        if len(options) > 0:
            options_str = '&'.join(options)
            url += f'?{options_str}'

        return url

    @staticmethod
    def table_url(
        coordinates: list[tuple],
        mode: str = 'driving',
        **kwargs
    ) -> str:
        """
        Calculate the duration of the fastest route between all pairs of the supplied coordinates.

        Args:
            host (str): The host URL.
            port (int): The port number.
            coordinates (list): A list of coordinates in the form [(lon1, lat1), (lon2, lat2), ...].
            mode (str, optional): The mode of transportation. One of driving, walking, cycling.
            annotations (str, optional): Returns additional metadata for each coordinate along the
                route geometry. One of true, false, nodes, distance, duration, datasources, weight,
                speed.
            sources (list, optional): Use location with given index as source.
            destinations (list, optional): Use location with given index as destination.

        Returns:
            str: A URL string for the table service.
        """

        # Set default kwargs
        defaults = {
            'annotations': 'duration',
            'sources': None,
            'destinations': None
        }
        for key, value in defaults.items():
            kwargs.setdefault(key, value)

        # Required keyword arguments
        host = kwargs['host']
        port = kwargs['port']

        assert mode in ['driving', 'walking', 'cycling'], \
            'mode must be one of "driving", "walking", or "cycling"'

        # Annotations must be either duration, distance, or duration and distance
        assert kwargs['annotations'] in ['duration', 'distance'], \
            'annotations must be one of "duration", "distance"'

        # List args
        list_args = {'sources': kwargs['sources'], 'destinations': kwargs['destinations']}

        # Option args
        option_args = {'annotations': kwargs['annotations']}

        return URLQueries.url_constructor(host, port, mode, coordinates, list_args, option_args)

    @staticmethod
    def match_url(
        coordinates: list[tuple],
        mode: str = 'driving',
        **kwargs
    ) -> str:
        """
        This function matches supplied coordinates to the road network and returns
        the nearest road segment for each point.

        Args:
            host (str): The host URL.
            port (int): The port number.
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
            str: A URL string for the match service.
        """

        # Set default kwargs
        defaults = {
            'geometries': 'polyline',
            'annotations': 'false',
            'radiuses': None,
            'waypoints': None,
            'gaps': False,
            'tidy': False,
            'steps': False,
            'dt_format': '%Y-%m-%d %H:%M:%S%z'
        }

        for key, value in defaults.items():
            kwargs.setdefault(key, value)

        # Required keyword arguments
        host = kwargs['host']
        port = kwargs['port']

        assert mode in ['driving', 'walking', 'cycling'], \
            'mode must be one of "driving", "walking", or "cycling"'

        # Process timestamps if they are strings
        if isinstance(kwargs['timestamps'], list):
            # If timestamp is a string, convert to a list of integers
            kwargs['timestamps'] = [
                parse_datetime_to_int(t, kwargs['dt_format']) for t in kwargs['timestamps']
                ]

        # List args
        list_args = {
            'timestamps': kwargs['timestamps'],
            'radiuses': kwargs['radiuses'],
            'waypoints': kwargs['waypoints']
        }

        # Option args
        option_args = {
            'geometries': kwargs['geometries'],
            'annotations': kwargs['annotations'],
            'gaps': kwargs['gaps'],
            'tidy': kwargs['tidy'],
            'steps': kwargs['steps']
        }

        # Construct base URL
        return URLQueries.url_constructor(host, port, mode, coordinates, list_args, option_args)

    @staticmethod
    def route_url(
        coordinates: list[tuple],
        mode: str = 'driving',
        **kwargs
    ) -> str:
        """
        This function returns the fastest route between the supplied coordinates.

        Args:
            host (str): The host URL.
            port (int): The port number.
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
            str: A URL string for the route service.
        """

        # Set default kwargs
        defaults = {
            'geometries': 'polyline',
            'steps': False,
            'alternatives': None,
            'continue_straight': False,
            'annotations': 'duration',
            'waypoints': None
        }
        for key, value in defaults.items():
            kwargs.setdefault(key, value)

        # Required keyword arguments
        host = kwargs['host']
        port = kwargs['port']

        # List args
        list_args = {'waypoints': kwargs['waypoints']}

        # Option args
        option_args = {
            'geometries': kwargs['geometries'],
            'steps': kwargs['steps'],
            'alternatives': kwargs['alternatives'],
            'continue_straight': kwargs['continue_straight'],
            'annotations': kwargs['annotations']
        }

        return URLQueries.url_constructor(host, port, mode, coordinates, list_args, option_args)
