# import redis
# import requests
# import json

# # Connect to Redis Cloud
# redis_host = 'redis-19074.c241.us-east-1-4.ec2.redns.redis-cloud.com'
# redis_port = 19074
# redis_password = 'xBrz8lzAfBFXSlxD3opqbvxAzwwkquqE'

# redis_client = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

# # Fetch Data from Nobel Prize API
# url = "https://api.nobelprize.org/v1/prize.json"
# response = requests.get(url)
# if response.status_code == 200:
#     prizes = response.json()["prizes"]
# else:
#     print("Failed to fetch data from the API")
#     exit()

# # Filter Data from 2013 to 2023
# filtered_prizes = [prize for prize in prizes if 2013 <= int(prize["year"]) <= 2023]

# # Clean and Upload Filtered Data to Redis as JSON Objects
# for prize in filtered_prizes:
#     # Ensure 'year' is an integer
#     prize['year'] = int(prize['year'])
    
#     # # Fix motivation fields to remove escaped quotes and double quotes
#     # for laureate in prize.get("laureates", []):
#     #     if "motivation" in laureate:
#     #         # Remove any escape sequences like \" and unnecessary double quotes
#     #         cleaned_motivation = laureate["motivation"].replace('\\"', '"').replace('""', '"')
#     #         # Also handle quotes at the start and end of the string
#     #         cleaned_motivation = cleaned_motivation.strip('"')
#     #         laureate["motivation"] = cleaned_motivation

#     # Create a unique key for each prize (e.g., prizes:2013:1)
#     key = f"prizes:{prize['year']}:{prize.get('category', 'unknown')}"
#     # Store the cleaned data as JSON using RedisJSON
#     redis_client.execute_command("JSON.SET", key, ".", json.dumps(prize))

# print("Data successfully cleaned and uploaded to Redis!")
import redis
import requests
import json

# Connect to Redis Cloud
redis_host = 'redis-19074.c241.us-east-1com'
redis_port = 19
redis_password = 'xBrz8lzvxAzwwkquqE'

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
    
    # Create a unique key for each prize (e.g., prizes:2013:1)
    key = f"prizes:{prize['year']}:{prize.get('category', 'unknown')}"
    # Store the cleaned data as JSON using RedisJSON
    redis_client.execute_command("JSON.SET", key, ".", json.dumps(prize))

print("Data successfully cleaned and uploaded to Redis!")

# Create an index for querying the data using RediSearch
# Drop index if it already exists
try:
    redis_client.execute_command("FT.DROPINDEX", "prizeIndex")
except:
    pass  # Ignore if the index doesn't exist

# Define the schema for the index
redis_client.execute_command(
    "FT.CREATE", "prizeIndex", "ON", "JSON", "PREFIX", "1", "prizes:",
    "SCHEMA",
    "$.year", "AS", "year", "NUMERIC",
    "$.category", "AS", "category", "TAG",
    "$.laureates[*].firstname", "AS", "firstname", "TEXT",
    "$.laureates[*].surname", "AS", "surname", "TEXT",
    "$.laureates[*].motivation", "AS", "motivation", "TEXT"
)

print("Index created successfully!")

# Query 1: Total number of laureates for a given category between a specified year range
def count_laureates_by_category(category, start_year, end_year):
    query = f"@category:{{{category}}} @year:[{start_year} {end_year}]"
    result = redis_client.execute_command("FT.SEARCH", "prizeIndex", query, "NOCONTENT")
    return result[0]  # First element is the count

# Query 2: Total number of laureates whose motivation contains a given keyword
def count_laureates_by_keyword(keyword):
    query = f"@motivation:*{keyword}*"
    result = redis_client.execute_command("FT.SEARCH", "prizeIndex", query, "NOCONTENT")
    return result[0]

# Query 3: Get the year, category, and motivation for a given first and last name
def get_laureate_details(firstname, surname):
    query = f"@firstname:{firstname} @surname:{surname}"
    result = redis_client.execute_command("FT.SEARCH", "prizeIndex", query)
    if len(result) > 1:
        return result[1:]  # Return the matched records
    else:
        return None

# Example Queries
print("Query 1: Total laureates in Physics between 2013 and 2018: ",
      count_laureates_by_category("physics", 2013, 2018))
print("Query 2: Total laureates with 'peace' in motivation: ",
      count_laureates_by_keyword("peace"))
print("Query 3: Details of laureate with first name 'Alice' and surname 'Munro': ",
      get_laureate_details("Alice", "Munro"))
