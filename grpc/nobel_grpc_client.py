import grpc
import nobel_prize_pb2
import nobel_prize_pb2_grpc

def run():
    # Establish a connection with the gRPC server
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = nobel_prize_pb2_grpc.NobelServiceStub(channel)
    # Replace 'localhost:50051' with your cloud endpoint
    # with grpc.insecure_channel('https://grpc-server-client.victoriousfield-b092448d.canadaeast.azurecontainerapps.io') as channel:
    #     stub = nobel_prize_pb2_grpc.NobelServiceStub(channel)


        # 1. Query 1: Count laureates by category
        print("Running Query 1: Count Laureates By Category (Physics, 2013-2023)...")
        response = stub.CountLaureatesByCategory(
            nobel_prize_pb2.CategoryRequest(category="physics", start_year=2013, end_year=2023)
        )
        print(f"Total laureates in Physics (2013-2023): {response.count}\n")

        # 2. Query 2: Count laureates by keyword in motivation
        print("Running Query 2: Count Laureates By Keyword (Keyword: 'peace')...")
        response = stub.CountLaureatesByKeyword(nobel_prize_pb2.KeywordRequest(keyword="peace"))
        print(f"Total laureates with 'peace' in motivation: {response.count}\n")

        # 3. Query 3: Get laureate details by name
        print("Running Query 3: Get Laureate Details (Firstname: 'Arieh', Surname: 'Warshel')...")
        response = stub.GetLaureateDetails(nobel_prize_pb2.LaureateRequest(firstname='Alice', surname='Munro'))
        if response.laureate_details:
            for detail in response.laureate_details:
                print(f"Year: {detail.year}, Category: {detail.category}, Motivation: {detail.motivation}")
        else:
            print("No details found for the specified laureate.")

if __name__ == "__main__":
    run()
