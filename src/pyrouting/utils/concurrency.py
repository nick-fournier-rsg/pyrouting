"""
This module contains the ConcurrentRequests class,
which is used to make concurrent requests to the OSRM server.
"""
import json
import asyncio
import aiohttp
from tqdm.asyncio import tqdm_asyncio


class ConcurrentRequests:
    """
    This class is used to make concurrent requests to the OSRM server.
    """
    connector: aiohttp.TCPConnector

    def __init__(
        self,
        parallel_requests: int = 250,
        limit: int = 0,
        limit_per_host: int = 500,
        ttl_dns_cache: int = 300,
        **kwargs
    ) -> None:
        """
        Initialize the ConcurrentRequests object.

        Args:
            parallel_requests (int): The number of parallel requests.
            limit (int): The total limit of parallel connections.
            limit_per_host (int): The limit of parallel connections per host.
            ttl_dns_cache (int): The time-to-live of the DNS cache.
            **kwargs: Additional keyword arguments for aiohttp.TCPConnector.
        """
        self.parallel_requests = parallel_requests
        self.limit = limit
        self.limit_per_host = limit_per_host
        self.ttl_dns_cache = ttl_dns_cache
        self.kwargs = kwargs

    def open_connector(self) -> None:
        """
        Connect to the OSRM server and initialize the aiohttp TCPConnector object.
        """
        kwargs = self.kwargs
        kwargs.update({
            'limit_per_host': self.limit_per_host,
            'limit': self.limit,
            'ttl_dns_cache': self.ttl_dns_cache
        })
        self.connector = aiohttp.TCPConnector(**kwargs)

    def close_connector(self) -> None:
        """
        Close the connection to the OSRM server.
        """
        self.connector.close()

    async def async_gather(self, urls: list[str]) -> list:
        """
        This is a helper function to make concurrent GET requests to the OSRM server.

        Args:
            urls (list[str]): A list of URLs.

        Returns:
            list: A list of JSON responses.
        """

        # Check if connection is open
        if not hasattr(self, 'connector') or self.connector.closed:
            self.open_connector()

        semaphore = asyncio.Semaphore(self.parallel_requests)
        session = aiohttp.ClientSession(connector=self.connector)
        results = []

        # heres the logic for the generator
        async def get(url):
            async with semaphore:
                async with session.get(url, ssl=False) as response:
                    obj = json.loads(await response.read())
                    results.append(obj)

        # async gather with tqdm progress bar
        await tqdm_asyncio.gather(*(get(url) for url in urls))
        # await asyncio.gather(*(get(url) for url in urls))
        await session.close()

        return results

    def get(
        self,
        urls: list[str],
        keep_open: bool = False
    ):
        """
        Make concurrent GET requests to the OSRM server.

        Args:
            urls (list[str]): A list of URLs.
            keep_open (bool): Keep the connection open. Defaults to False.

        Returns:
            list: A list of JSON responses.
        """

        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(self.async_gather(urls))

        if keep_open:
            self.close_connector()

        return results
