import time

import pytest

from app.core.exceptions import RateLimitExceeded
from app.services.rate_limiter import RateLimiter


class FakePipeline:
    def __init__(self, redis):
        self.redis = redis
        self.ops = []

    def incr(self, key):
        self.ops.append(("incr", key))
        return self

    def expire(self, key, ttl):
        self.ops.append(("expire", key, ttl))
        return self

    async def execute(self):
        for op in self.ops:
            if op[0] == "incr":
                key = op[1]
                self.redis.store[key] = str(int(self.redis.store.get(key, "0")) + 1)
            elif op[0] == "expire":
                key = op[1]
                ttl = op[2]
                self.redis.ttls[key] = ttl
        self.ops.clear()


class FakeRedis:
    def __init__(self):
        self.store = {}
        self.ttls = {}
        self.hashes = {}

    async def get(self, key):
        return self.store.get(key)

    async def ttl(self, key):
        return self.ttls.get(key, -1)

    def pipeline(self):
        return FakePipeline(self)

    async def hgetall(self, key):
        return self.hashes.get(key, {})

    async def hset(self, key, mapping):
        self.hashes[key] = dict(mapping)

    async def expire(self, key, ttl):
        self.ttls[key] = ttl


@pytest.mark.asyncio
async def test_check_rate_limit_blocks_after_threshold():
    redis = FakeRedis()
    limiter = RateLimiter(redis)

    await limiter.check_rate_limit("key1", limit=2, window_seconds=60)
    await limiter.check_rate_limit("key1", limit=2, window_seconds=60)

    with pytest.raises(RateLimitExceeded):
        await limiter.check_rate_limit("key1", limit=2, window_seconds=60)


@pytest.mark.asyncio
async def test_token_bucket_consumes_and_refills():
    redis = FakeRedis()
    limiter = RateLimiter(redis)

    await limiter.consume_token("bucket", capacity=2, refill_rate_per_second=1.0)
    await limiter.consume_token("bucket", capacity=2, refill_rate_per_second=1.0)
    with pytest.raises(RateLimitExceeded):
        await limiter.consume_token("bucket", capacity=2, refill_rate_per_second=1.0)

    # Simulate refill by adjusting stored timestamp.
    old = dict(redis.hashes["bucket:bucket"])
    old["ts"] = str(time.time() - 2.0)
    old["tokens"] = "0"
    redis.hashes["bucket:bucket"] = old

    await limiter.consume_token("bucket", capacity=2, refill_rate_per_second=1.0)
