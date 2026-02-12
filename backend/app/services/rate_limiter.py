from __future__ import annotations

import math
import time

from redis.asyncio import Redis

from app.core.exceptions import RateLimitExceeded


class RateLimiter:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def check_rate_limit(self, key: str, limit: int, window_seconds: int) -> None:
        current = await self.redis.get(key)
        if current and int(current) >= limit:
            ttl = await self.redis.ttl(key)
            raise RateLimitExceeded(f"Rate limit exceeded. Retry in {max(ttl, 1)}s")

        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, window_seconds)
        await pipe.execute()

    async def consume_token(
        self,
        key: str,
        capacity: int,
        refill_rate_per_second: float,
    ) -> None:
        """
        Redis-backed token bucket.
        Stores state as hash:
        - tokens: float
        - ts: epoch seconds
        """
        bucket_key = f"bucket:{key}"
        now = time.time()

        data = await self.redis.hgetall(bucket_key)
        tokens = float(data.get("tokens", capacity))
        last_ts = float(data.get("ts", now))

        elapsed = max(0.0, now - last_ts)
        tokens = min(capacity, tokens + elapsed * refill_rate_per_second)

        if tokens < 1.0:
            wait = math.ceil((1.0 - tokens) / max(refill_rate_per_second, 0.0001))
            raise RateLimitExceeded(f"Token bucket exhausted. Retry in {wait}s")

        tokens -= 1.0
        await self.redis.hset(bucket_key, mapping={"tokens": str(tokens), "ts": str(now)})
        await self.redis.expire(bucket_key, 3600)
