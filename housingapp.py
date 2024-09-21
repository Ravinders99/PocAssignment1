from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis

app = FastAPI()

# Connect to Redis (ensure these credentials are correct)
redis_client = redis.Redis(
    host='redis-19074.c241.us-east-1-4.ec2.redns.redis-cloud.com',
    port=19074,
    password='xBrz8lzAfBFXSlxD3opqbvxAzwwkquqE',
    decode_responses=True  # Automatically decode responses to strings
)

# Define the structure for setting data
class RedisData(BaseModel):
    key: str
    field: str
    value: str

@app.get("/data/{key}")
def get_data(key: str):
    """Get the full hash data for a key"""
    if not redis_client.exists(key):
        raise HTTPException(status_code=404, detail=f"Key '{key}' not found")

    # Get all fields and values in the hash
    data = redis_client.hgetall(key)
    if not data:
        raise HTTPException(status_code=404, detail=f"No data found for key '{key}'")

    return {key: data}

@app.get("/data/{key}/{field}")
def get_data_field(key: str, field: str):
    """Get a specific field from the hash for a key"""
    if not redis_client.exists(key):
        raise HTTPException(status_code=404, detail=f"Key '{key}' not found")
    
    value = redis_client.hget(key, field)
    if value is None:
        raise HTTPException(status_code=404, detail=f"Field '{field}' not found in key '{key}'")

    return {field: value}

@app.post("/data/")
def set_data(redis_data: RedisData):
    """Set a field in the hash for a given key"""
    redis_client.hset(redis_data.key, redis_data.field, redis_data.value)
    return {"message": f"Field '{redis_data.field}' set for key '{redis_data.key}'"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
