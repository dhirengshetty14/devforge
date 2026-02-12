import json
from collections.abc import AsyncGenerator

from redis.asyncio import Redis


def generation_channel(job_id: str) -> str:
    return f"generation:{job_id}"


async def publish_generation_event(redis_client: Redis, job_id: str, payload: dict) -> None:
    await redis_client.publish(generation_channel(job_id), json.dumps(payload))


async def generation_event_stream(redis_client: Redis, job_id: str) -> AsyncGenerator[dict, None]:
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(generation_channel(job_id))
    try:
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            try:
                yield json.loads(message["data"])
            except Exception:
                continue
    finally:
        await pubsub.unsubscribe(generation_channel(job_id))
        await pubsub.close()
