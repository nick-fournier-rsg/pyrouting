"""
This is a test module for the PyOSRM class.
"""

import pytest
from pyosrm import PyOSRM


coords = [
    (47.66117, -122.31197),
    (47.66135, -122.31247),
    (47.66128, -122.31293),
    (47.66148, -122.31288),
    (47.662, -122.3132)
]
times = [
    "2023-04-26 01:31:55+0000", "2023-04-26 01:32:22+0000", "2023-04-26 01:32:45+0000",
    "2023-04-26 01:33:05+0000", "2023-04-26 01:33:37+0000"
    ]
modes = ['driving']
geos = ['polyline', 'geojson', 'polyline6']

# Create a PyOSRM object
PYOSRM = PyOSRM(host='192.168.1.126')


@pytest.mark.parametrize("coordinates", [coords])
@pytest.mark.parametrize("mode", modes)
def test_table_service(coordinates, mode):
    """
    This function tests the table service of the PyOSRM class.
    """
    response = PYOSRM.table(coordinates, mode)

    assert response['code'] == 'Ok'


@pytest.mark.parametrize("coordinates", [coords])
@pytest.mark.parametrize("mode", modes)
@pytest.mark.parametrize("timestamps", times)
@pytest.mark.parametrize("geometries", geos)
def test_match_service(coordinates, mode, timestamps, geometries):
    """
    This function tests the match service of the PyOSRM class.
    """

    response = PYOSRM.match(coordinates, mode, timestamps, geometries=geometries)

    assert response['code'] == 'Ok'


@pytest.mark.parametrize("coordinates", [[coords[0], coords[-1]]])
@pytest.mark.parametrize("mode", modes)
@pytest.mark.parametrize("geometries", geos)
def test_route_service(coordinates, mode, geometries):
    """
    This function tests the route service of the PyOSRM class.
    """

    response = PYOSRM.route(coordinates, mode, geometries=geometries)

    assert response['code'] == 'Ok'


if __name__ == '__main__':
    test_table_service(coords, 'driving')
    test_match_service(coords, 'driving', times, 'polyline')
    test_route_service([coords[0], coords[-1]], 'driving', geometries='polyline')
