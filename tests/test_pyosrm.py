"""
This is a test module for the PyOSRM class.
"""

from pyosrm import PyOSRM


# Create a PyOSRM object
PYOSRM = PyOSRM(host='192.168.1.126')


def test_table_service():
    """
    This function tests the table service of the PyOSRM class.
    """

    response = PYOSRM.table([(37.7749, -122.4194), (34.0522, -118.2437), (40.7128, -74.0060)])

    assert response['code'] == 'Ok'


def test_match_service():
    """
    This function tests the match service of the PyOSRM class.
    """

    coords = [(37.7749, -122.4194), (34.0522, -118.2437), (40.7128, -74.0060)]
    timestamps = [0, 60, 120]

    response = PYOSRM.match(coords, timestamps=timestamps)

    assert response['code'] == 'Ok'


def test_route_service():
    """
    This function tests the route service of the PyOSRM class.
    """

    response = PYOSRM.route([(37.7749, -122.4194), (34.0522, -118.2437), (40.7128, -74.0060)])

    assert response['code'] == 'Ok'


if __name__ == '__main__':
    test_table_service()
    test_match_service()
    test_route_service()
