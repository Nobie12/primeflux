import redis
from django.conf import settings


class RedisClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)

            cls._instance.client = redis.Redis(
                host=getattr(settings, "REDIS_HOST", "localhost"),
                port=int(getattr(settings, "REDIS_PORT", 6379)),
                db=int(getattr(settings, "REDIS_DB", 0)),
                decode_responses=True,  # 4. Converts bytes to strings automatically
            )

        return cls._instance

    def ping(self):
        """Verify if the Redis service is online and reachable."""
        try:
            return self.client.ping()
        except (redis.ConnectionError, redis.TimeoutError):
            return False

    def set(self, key, value, ex=None):
        """Set a value in Redis with an optional expiration time."""
        self.client.set(name=key, value=value, ex=ex)

    def get(self, key):
        """Get a value from Redis."""
        return self.client.get(name=key)

    def delete(self, key):
        """Delete a key from Redis."""
        self.client.delete(key)

    def get_ttl(self, key):
        """Get the time-to-live (TTL) of a key in seconds."""
        return self.client.ttl(key)
