import grpc
import json
import redis
import nobel_prize_pb2
import nobel_prize_pb2_grpc

# Connect to Redis
redis_client = redis.StrictRedis(
    host='redis-17203.c251.east-us-mz.azure.redns.redis-cloud.com',  # Replace with your Redis host
    port=17203,     # Replace with your Redis port
    password='WkGWYEDSqarBqAphhlBxe7XjnLx81qaL',  # Replace with your Redis password
    decode_responses=True
)

def create_index():
    # Create an index on the fields 'year' and 'category', with 'laureates' as vector type
    redis_client.execute_command("""
        FT.CREATE idx:prizes ON JSON
        SCHEMA $.year AS year NUMERIC
               $.category AS category TAG
               $.laureates[*].firstname AS firstname TAG
               $.laureates[*].surname AS surname TAG
               $.laureates[*].motivation AS motivation TAG
    """)

class NobelPrizeService(nobel_prize_pb2_grpc.NobelPrizeServiceServicer):

    def GetLaureatesByYearCategory(self, request, context):
        category = request.category
        start_year = request.start_year
        end_year = request.end_year

        # Query Redis for laureates
        total_laureates = 0
        for year in range(start_year, end_year + 1):
            key = f"prizes:{year}:{category}"
            result = redis_client.json().get(key)
            if result:
                prize_data = json.loads(result)
                total_laureates += len(prize_data.get('laureates', []))

        return nobel_prize_pb2.YearCategoryResponse(total_laureates=total_laureates)

    def GetLaureatesByKeyword(self, request, context):
        keyword = request.keyword
        # Search in Redis for motivations containing the keyword
        search_response = redis_client.execute_command(
            "FT.SEARCH",
            "idx:prizes",
            f"@motivation:*{keyword}*",
            "RETURN", "0"
        )

        total_laureates = search_response[0]  # The first element is the total count of matches
        return nobel_prize_pb2.KeywordResponse(total_laureates=total_laureates)

    def GetLaureateDetails(self, request, context):
        first_name = request.first_name
        last_name = request.last_name

        # Search in Redis for the laureate by name
        search_response = redis_client.execute_command(
            "FT.SEARCH",
            "idx:prizes",
            f"@firstname:{{{first_name}}} @surname:{{{last_name}}}",
            "RETURN", "0"
        )

        # Assuming we only want the first match
        if search_response and len(search_response) > 1:
            key = search_response[1]  # Get the key of the first match
            laureate_data = redis_client.json().get(key)
            if laureate_data:
                prize_data = json.loads(laureate_data)
                motivation = prize_data['laureates'][0]['motivation'] if prize_data['laureates'] else "No motivation available"
                return nobel_prize_pb2.LaureateResponse(
                    year=prize_data['year'],
                    category=prize_data['category'],
                    motivation=motivation
                )

        return nobel_prize_pb2.LaureateResponse()

def serve():
    # Create the index when the server starts
    create_index()

    server = grpc.server()
    nobel_prize_pb2_grpc.add_NobelPrizeServiceServicer_to_server(NobelPrizeService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
