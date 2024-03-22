"""
This is a test module for the PyOSRM class.
"""

import pytest
import pandas as pd
from pyrouting.osrm import OSRMQueries
from pyrouting import utils

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


# Load sample data
locations = pd.read_csv('tests/sample_locations.csv')


# Create a PyOSRM object
PYOSRM = OSRMQueries(host='192.168.1.126', port=5000)
HOST_ALIVE = utils.testhost(PYOSRM.host, PYOSRM.port)


@pytest.mark.skipif(not HOST_ALIVE, reason="Host is not reachable")
@pytest.mark.parametrize("coordinates", [coords])
@pytest.mark.parametrize("mode", modes)
def test_table_service(coordinates, mode):
    """
    This function tests the table service of the PyOSRM class.
    """
    response = PYOSRM.table(coordinates, mode)

    assert response['code'] == 'Ok'


@pytest.mark.skipif(not HOST_ALIVE, reason="Host is not reachable")
@pytest.mark.parametrize("coordinates", [coords])
@pytest.mark.parametrize("mode", modes)
@pytest.mark.parametrize("timestamps", times)
@pytest.mark.parametrize("geometries", geos)
def test_match_service(coordinates, mode, timestamps, geometries):
    """
    This function tests the match service of the PyOSRM class.
    """

    response = PYOSRM.match(coordinates, timestamps, mode, geometries)

    assert response['code'] == 'Ok'


@pytest.mark.skipif(not HOST_ALIVE, reason="Host is not reachable")
@pytest.mark.parametrize("coordinates", [[coords[0], coords[-1]]])
@pytest.mark.parametrize("mode", modes)
@pytest.mark.parametrize("geometries", geos)
def test_route_service(coordinates, mode, geometries):
    """
    This function tests the route service of the PyOSRM class.
    """

    response = PYOSRM.route(coordinates, mode, geometries=geometries)

    assert response['code'] == 'Ok'


@pytest.mark.skipif(not HOST_ALIVE, reason="Host is not reachable")
@pytest.mark.parametrize("df", [locations])
def test_df_matching(df):
    """
    This function tests the bulk matching service of the PyOSRM class.
    """
    kwargs = {
        'mode': 'driving',
        'group_col': 'trip_id',
        'renames': {'collect_time': 'timestamp'},
        'geometries': 'polyline6',
        'unpack': ['geometry', 'confidence', 'distance', 'duration', 'waypoints']
    }
    response_df = PYOSRM.match_df(df, **kwargs)

    assert isinstance(response_df, pd.DataFrame)
    assert response_df.geometry.notnull().any()


if __name__ == '__main__':
    test_df_matching(locations.iloc[:10000])
    test_table_service(coords, 'driving')
    test_match_service(coords, 'driving', times, 'polyline6')
    test_route_service([coords[0], coords[-1]], 'driving', geometries='polyline6')
