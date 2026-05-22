import logging

log = logging.getLogger(__name__)


HAS_REDIS = False
try:
    import redis

    HAS_REDIS = True
except ImportError as e:
    _ = e

if HAS_REDIS:

    class RedisCache:
        def __init__(
            self,
            *,
            verbose: bool = False,
            host: str = "localhost",
            port: int = 6379,
            db: int = 0,
        ) -> None:
            self.verbose = verbose

            self.pool = redis.ConnectionPool(host=host, port=port, db=db, decode_responses=True)
            self.redis = redis.Redis(
                connection_pool=self.pool,
            )

        def get(
            self,
            keyString: str,
        ) -> str | None:
            data = self.redis.get(keyString)
            if data:
                return str(data)
            return None

        def put(
            self,
            keyString: str,
            data: str,
        ) -> str:
            self.redis.set(
                keyString,
                bytes(data, "utf-8"),
            )

            return data
