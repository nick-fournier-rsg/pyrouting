"""
General utility functions.
"""
from datetime import datetime


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
