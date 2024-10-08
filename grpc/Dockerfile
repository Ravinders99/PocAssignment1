# Use an official Python runtime as the base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy all the files in the current directory to the container
COPY . .

# Install the required packages
RUN pip install --no-cache-dir grpcio grpcio-tools redis requests

# Expose the gRPC port
EXPOSE 50051

# Run the gRPC server
CMD ["python", "nobel_grpc_server.py"]
