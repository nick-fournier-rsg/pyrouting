"""
This module contains functions for unpacking the JSON response from the OSRM API.
"""
from typing import Iterator
import numpy as np


def _unpack(matchings, unpack) -> Iterator:
    """
    This is a generator function that unpacks the matchings dictionary based on the unpack list.

    Args:
        matchings (_type_): _description_
        unpack (_type_): _description_

    Yields:
        _type_: _description_
    """
    for key in unpack:
        yield matchings.get(key)


def unpack_match(response: dict, unpack: list[str]) -> Iterator:
    """
    This function unpacks the JSON response from the OSRM API, extracting the specified attributes
    and returns them as a flat dictionary. This makes it easier to optionally convert the JSON
    response to a pandas DataFrame.

    Args:
        response (dict): The JSON response from the OSRM API.
        filter (list): A list of attributes to extract from the JSON response.

    Returns:
        tuple: A tuple of the extracted attributes.

    """

    # Extract the matchings
    matchings = response.get('matchings', [])

    if len(matchings) == 1:
        matchings = matchings[0]
        return _unpack(matchings, unpack)

    # If more than one matching, choose the highest confidence
    if len(matchings) > 1:
        confidences = [m['confidence'] for m in matchings]
        idx = np.argmax(confidences)
        matchings = matchings[idx]
        return _unpack(matchings, unpack)

    # If no matchings, return generator of None
    return _unpack({}, unpack)
