import threading

import redis

from odoo.tools import config

# Module-level variables for the Redis connection and lock
_redis_client = None
_redis_lock = threading.Lock()


def get_redis_connection():
    """Get or create a singleton Redis connection."""
    global _redis_client

    if _redis_client is None:
        with _redis_lock:
            # Double-check to avoid race conditions
            if _redis_client is None:
                try:
                    redis_host = config.get('redis_host', 'localhost')
                    redis_port = int(config.get('redis_port', 6379))
                    redis_db = int(config.get('redis_db', 0))
                    redis_password = config.get('redis_password', None)

                    # Use a connection pool for better performance
                    pool = redis.ConnectionPool(
                        host=redis_host,
                        port=redis_port,
                        db=redis_db,
                        password=redis_password,
                        decode_responses=True,
                        max_connections=50,
                    )

                    _redis_client = redis.Redis(connection_pool=pool)

                    # Test the connection
                    _redis_client.ping()
                except Exception as e:
                    # Chaining the original error (e) to the new one
                    raise Exception(f"Failed to connect to Redis: {e}") from e

    return _redis_client
