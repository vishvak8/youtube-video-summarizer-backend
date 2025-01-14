# Use the official Python 3.10.12 base image
FROM python:3.10.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Expose the port the app runs on
EXPOSE 5001

# Command to run the application
CMD ["waitress-serve", "--host=0.0.0.0", "--port=5001", "fetch_transcript:app"]
