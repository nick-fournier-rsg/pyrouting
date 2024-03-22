"""
This snippet is a class that provides helper functions for connection testing.
"""
import requests


# If this grows, consider moving to a class
def testhost(host: str, port: str | int) -> bool:
    """
    Test the host URL.

    Returns:
        bool: True if the host is reachable, False otherwise.
    """

    # Test the host URL
    url = f'{host}:{port}'
    try:
        requests.head(url, timeout=5)
        return True
    except requests.exceptions.ConnectionError:
        return False
