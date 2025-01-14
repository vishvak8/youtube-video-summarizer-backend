# Use the official Python 3.10.12 base image
FROM python:3.10.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir Flask==3.1.0 Flask-Cors==5.0.0 flatbuffers==24.12.23 \
    waitress==3.0.2 youtube-transcript-api==0.6.3 transformers==4.48.0 \
    requests==2.32.3 torchvision==0.20.1 torchaudio==2.5.1 torch==2.5.1 huggingface-hub==0.27.1

# Copy the rest of the application code to the container
COPY . .

# Expose the port the app runs on
EXPOSE 5001

# Command to run the application
CMD ["waitress-serve", "--host=0.0.0.0", "--port=5001", "fetch_transcript:app"]
