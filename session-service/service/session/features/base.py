from service.session.core.management import InitRedis

"""
BaseSession class for initializing the Redis client.

This class provides a method to ping the Redis server and check if it is reachable.

Attributes:
    redis (AsyncRedis): Asynchronous Redis client instance
"""


class BaseSession:
    """
    BaseSession class for initializing the Redis client.

    This class provides a method to ping the Redis server and check if it is reachable.

    Attributes:
        redis (AsyncRedis): Asynchronous Redis client instance
    """

    def __init__(self):
        self.redis = InitRedis()

    async def ping_test(self):
        if not await self.redis.ping():
            raise Exception("Redis connection failed")
        else:
            return True
