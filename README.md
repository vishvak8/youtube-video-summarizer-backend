# YouTube Video Summarizer - Backend
This Flask-based backend service powers the YouTube Video Summarizer application. It accepts a YouTube video URL, extracts the transcript, summarizes it using Hugging Face's BART model, and saves the generated summary into a Nhost database using GraphQL.

## What the backend does
- Accepts YouTube video URLs through a POST API
- Extracts transcripts using youtube-transcript-api
- Cleans and splits the transcript text
- Summarizes the content using Hugging Face's facebook/bart-large-cnn model
- Saves the summaries into a Nhost GraphQL database
- Handles errors for unavailable videos, missing transcripts, or invalid URLs

## Tech and Concepts Used
- Backend: Python with Flask
- Model: Hugging Face Transformers (facebook/bart-large-cnn)
- Database: Nhost GraphQL
- Libraries:
  - flask
  - flask-cors
  - requests
  - transformers
  - youtube-transcript-api
  - logging
  - re
  - urllib

## How to run the project
1. Clone the repository:
   
   git clone https://github.com/vishvak8/youtube-video-summarizer-backend.git

2. Navigate to the Backend directory:
   
   cd youtube-video-summarizer-backend

3. (Optional) Create a virtual environment:

   python3 -m venv venv
   source venv/bin/activate

4. Install the dependencies:

   pip install -r requirements.txt

5. Start the Flask server:

   python fetch_transcript.py

6. Access the backend server at:

   http://localhost:5001

## Notes
- The Nhost GraphQL URL and Admin Secret are already configured in the `app.py` file.
- Ensure the backend server is running before sending requests from the frontend.

## License
This project is open-source and intended for learning and demonstration purposes.


  
