import grpc
from concurrent import futures
import redis
import json
from grpc_nobel import nobel_prize_pb2
from grpc_nobel import nobel_prize_pb2_grpc

# Redis connection configuration
redis_host = 'redis-19074.c241.us-east-1-4.ec2.redns.redis-cloud.com'
redis_port = 19074
redis_password = 'xBrz8lzAfBFXSlxD3opqbvxAzwwkquqE'
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
        details = []

        # Parse the search results
        for i in range(2, len(result), 2):  # Skip metadata elements
            data = json.loads(result[i])
            for laureate in data.get("laureates", []):
                details.append(
                    nobel_prize_pb2.LaureateDetails(
                        year=data['year'],
                        category=data['category'],
                        motivation=laureate.get("motivation", "N/A")
                    )
                )
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
