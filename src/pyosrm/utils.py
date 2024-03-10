"""
General utility functions.
"""
from datetime import datetime
import functools
import requests


# decorator to request the url that the function returns
def make_request(func, timeout=5):
    """
    This decorator requests the URL that the function returns.

    Args:
        func (function): The function to decorate.
        timeout (int, optional): The timeout for the request. Defaults to 5.

    Returns:
        the JSON response from the URL.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> dict:
        # get the sub-function func + "_url"
        # func = getattr(func.__name__ + '_url')
        url = func(*args, **kwargs)
        response = requests.get(url, timeout=timeout)
        return response.json()
    return wrapper


def parse_datetime_to_int(timestamp: str | int | datetime, dt_format: str) -> int:
    """
    Parse a datetime object to an integer.

    Args:
        dt (datetime, str): The datetime object or string to parse.

    Returns:
        int: The integer representation of the datetime in total seconds since UNIX epoch.
    """

    if isinstance(timestamp, int):
        return timestamp

    elif isinstance(timestamp, str):
        return int(datetime.strptime(timestamp, dt_format).timestamp())

    elif isinstance(timestamp, datetime):
        # Get total seconds since UNIX epoch
        return int(timestamp.timestamp())

    else:
        raise ValueError('timestamp must be a string or datetime object')
