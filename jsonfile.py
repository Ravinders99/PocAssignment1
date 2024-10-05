import redis
import requests
import json

# Connect to Redis Cloud
redis_host = 'redis-19074.c241.us-east-1-4.ec2.redns.redis-cloud.com'
redis_port = 19074
redis_password = 'xBrz8lzAfBFXSlxD3opqbvxAzwwkquqE'

redis_client = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

# Fetch Data from Nobel Prize API
url = "https://api.nobelprize.org/v1/prize.json"
response = requests.get(url)
if response.status_code == 200:
    prizes = response.json()["prizes"]
else:
    print("Failed to fetch data from the API")
    exit()

# Filter Data from 2013 to 2023
filtered_prizes = [prize for prize in prizes if 2013 <= int(prize["year"]) <= 2023]

# Clean and Upload Filtered Data to Redis as JSON Objects
for prize in filtered_prizes:
    # Ensure 'year' is an integer
    prize['year'] = int(prize['year'])
    
    # Fix motivation fields to remove escaped quotes and double quotes
    for laureate in prize.get("laureates", []):
        if "motivation" in laureate:
            # Remove any escape sequences like \" and unnecessary double quotes
            cleaned_motivation = laureate["motivation"].replace('\\"', '"').replace('""', '"')
            # Also handle quotes at the start and end of the string
            cleaned_motivation = cleaned_motivation.strip('"')
            laureate["motivation"] = cleaned_motivation

    # Create a unique key for each prize (e.g., prizes:2013:1)
    key = f"prizes:{prize['year']}:{prize.get('category', 'unknown')}"
    # Store the cleaned data as JSON using RedisJSON
    redis_client.execute_command("JSON.SET", key, ".", json.dumps(prize))

print("Data successfully cleaned and uploaded to Redis!")
