import grpc
import nobel_prize_pb2
import nobel_prize_pb2_grpc


def run():
    # Establish a connection with the gRPC server
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = nobel_prize_pb2_grpc.NobelServiceStub(channel)

        # 1. Query 1: Count laureates by category
        response = stub.CountLaureatesByCategory(nobel_prize_pb2.CategoryRequest(category="physics", start_year=2013, end_year=2018))
        print(f"Total laureates in Physics (2013-2018): {response.count}")

        # 2. Query 2: Count laureates by keyword in motivation
        response = stub.CountLaureatesByKeyword(nobel_prize_pb2.KeywordRequest(keyword="peace"))
        print(f"Total laureates with 'peace' in motivation: {response.count}")

        # 3. Query 3: Get laureate details by name
        response = stub.GetLaureateDetails(nobel_prize_pb2.LaureateRequest(firstname="Alice", surname="Munro"))
        for detail in response.laureate_details:
            print(f"Year: {detail.year}, Category: {detail.category}, Motivation: {detail.motivation}")

if __name__ == "__main__":
    run()
