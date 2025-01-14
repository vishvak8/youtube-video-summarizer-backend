# Use the official Python 3.10.12 base image
FROM python:3.10.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 transformers==4.31.0 flask==2.2.5 flask-cors==3.0.10 waitress==2.1.2 youtube-transcript-api==0.4.5 requests==2.31.0

# Copy the rest of the application code to the container
COPY . .

# Expose the port the app runs on
EXPOSE 5001

# Command to run the application
CMD ["waitress-serve", "--host=0.0.0.0", "--port=5001", "fetch_transcript:app"]
