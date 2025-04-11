import redis.asyncio as redis
import json
from typing import Optional

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

async def get_from_cache(key: str) -> Optional[dict]:
    user = await redis_client.get(key)
    if user:
        return json.loads(user)
    return None

async def set_to_cache(key: str, data: dict, expire: int = 900):  
    await redis_client.set(key, json.dumps(data), ex=expire)
