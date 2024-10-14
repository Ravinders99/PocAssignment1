import grpc
import time
import csv  # Import CSV library for saving results
import nobel_prize_pb2
import nobel_prize_pb2_grpc


def measure_query_100_times(stub, request, query_function, query_name):
    """Run a query 100 times and measure the end-to-end delay for each run."""
    durations = []
    print(f"Running {query_name} 100 times...")

    for _ in range(100):
        start_time = time.time()  # Start the timer
        response = query_function(stub, request)
        end_time = time.time()    # End the timer

        # Calculate the duration and store it in milliseconds
        durations.append((end_time - start_time) * 1000)

    print(f"Completed {query_name} 100 times.\n")
    return durations


def save_to_csv(filename, data):
    """Save the duration data to a CSV file."""
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Run Number", "Duration (ms)"])
        for i, duration in enumerate(data):
            writer.writerow([i + 1, duration])


def count_laureates_by_category(stub, request):
    """Query to count laureates by category."""
    return stub.CountLaureatesByCategory(request)


def count_laureates_by_keyword(stub, request):
    """Query to count laureates by keyword in motivation."""
    return stub.CountLaureatesByKeyword(request)


def get_laureate_details(stub, request):
    """Query to get laureate details by name."""
    return stub.GetLaureateDetails(request)


def run():
    # with grpc.insecure_channel('https://grpc-server-01-ajbbaka7b5h8caeh.canadacentral-01.azurewebsites.net/') as channel:
    #     stub = nobel_prize_pb2_grpc.NobelServiceStub(channel)
    with grpc.insecure_channel('20.116.218.163:50051') as channel:
        stub = nobel_prize_pb2_grpc.NobelServiceStub(channel)

        # 1. Query 1: Count laureates by category
        category_request = nobel_prize_pb2.CategoryRequest(category="physics", start_year=2013, end_year=2023)
        category_durations = measure_query_100_times(stub, category_request, count_laureates_by_category, "Category Query")
        save_to_csv("category_query_durations.csv", category_durations)

        # 2. Query 2: Count laureates by keyword in motivation
        keyword_request = nobel_prize_pb2.KeywordRequest(keyword="peace")
        keyword_durations = measure_query_100_times(stub, keyword_request, count_laureates_by_keyword, "Keyword Query")
        save_to_csv("keyword_query_durations.csv", keyword_durations)

        # 3. Query 3: Get laureate details by name
        laureate_request = nobel_prize_pb2.LaureateRequest(firstname="Alice", surname="Munro")
        details_durations = measure_query_100_times(stub, laureate_request, get_laureate_details, "Details Query")
        save_to_csv("details_query_durations.csv", details_durations)

        print("Durations have been saved to CSV files.")
        return category_durations, keyword_durations, details_durations


if __name__ == "__main__":
    category_durations, keyword_durations, details_durations = run()
    print(f"Saved to CSV: category_query_durations.csv, keyword_query_durations.csv, details_query_durations.csv.")
