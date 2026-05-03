from __future__ import annotations
from Elara.workflows.cache import load_cache
from Elara.workflows.sync import load_storage


from storage.redis_engine import redis_client


async def prepare_runtime():
    await load_storage()
    await load_cache()
    await redis_client.connect()
