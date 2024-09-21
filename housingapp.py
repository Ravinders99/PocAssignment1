import os
import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Fetch Redis credentials from environment variables
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT')),
    password=os.getenv('REDIS_PASSWORD'),
    decode_responses=True
)

class RedisData(BaseModel):
    key: str
    field: str
    value: str

@app.get("/data/{key}")
def get_data(key: str):
    if not redis_client.exists(key):
        raise HTTPException(status_code=404, detail=f"Key '{key}' not found")
    data = redis_client.hgetall(key)
    return {key: data}
