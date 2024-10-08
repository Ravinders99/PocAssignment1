import grpc
from concurrent import futures
import redis
import json
import nobel_prize_pb2
import nobel_prize_pb2_grpc

# Redis connection configuration
redis_host = 'redis-19074.c2411-4.ec2.redns.redis-cloud.com'
redis_port = 1907
redis_password = 'xBrz8lXSlxD3opqbvxAzwwkquqE'
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

# Implement the NobelService Servicer
class NobelService(nobel_prize_pb2_grpc.NobelServiceServicer):
    def CountLaureatesByCategory(self, request, context):
        query = f"@category:{{{request.category}}} @year:[{request.start_year} {request.end_year}]"
        result = redis_client.execute_command("FT.SEARCH", "prizeIndex", query, "NOCONTENT")
        return nobel_prize_pb2.LaureateCountResponse(count=result[0])

    def CountLaureatesByKeyword(self, request, context):
        query = f"@motivation:*{request.keyword}*"
        result = redis_client.execute_command("FT.SEARCH", "prizeIndex", query, "NOCONTENT")
        return nobel_prize_pb2.LaureateCountResponse(count=result[0])

    def GetLaureateDetails(self, request, context):
        query = f"@firstname:{request.firstname} @surname:{request.surname}"
        result = redis_client.execute_command("FT.SEARCH", "prizeIndex", query)

        # Print the full result from Redis for debugging purposes
        print("Redis search result:", result)

        details = []

        # Ensure the Redis result has at least two elements (count and first result)
        if len(result) < 2:
            return nobel_prize_pb2.LaureateDetailsResponse(laureate_details=[])

        # Parse the search results
        for i in range(2, len(result), 2):  # Skip metadata elements (document IDs)
            json_data = result[i][1]  # This should be a JSON string , add [1]
            print(f"Processing entry {i}: {json_data}")  # Debug entry being processed
            try:
                # Try to load the JSON data
                data = json.loads(json_data)
                for laureate in data.get("laureates", []):
                    details.append(
                        nobel_prize_pb2.LaureateDetails(
                            year=data.get('year', "N/A"),
                            category=data.get('category', "N/A"),
                            motivation=laureate.get("motivation", "N/A")
                        )
                    )
            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON: {e}")
                return nobel_prize_pb2.LaureateDetailsResponse(laureate_details=[])
            except Exception as ex:
                print(f"An unexpected error occurred: {ex}")
                return nobel_prize_pb2.LaureateDetailsResponse(laureate_details=[])

        return nobel_prize_pb2.LaureateDetailsResponse(laureate_details=details)


# Function to start the gRPC server
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    nobel_prize_pb2_grpc.add_NobelServiceServicer_to_server(NobelService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC Server is running on port 50051...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
