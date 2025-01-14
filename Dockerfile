# Base image for Python
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy project files to the container
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Expose the port your app runs on (5001 in your case)
EXPOSE 5001

# Command to run your Flask app
CMD ["python", "app.py"]
