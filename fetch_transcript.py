from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from transformers import pipeline
from flask_cors import CORS
import requests
import re
import urllib.parse
import logging

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://youtube-video-summarizer-frontend.vercel.app"]}}, supports_credentials=True)

logging.basicConfig(level=logging.INFO)

# Helper to clean transcript
def clean_transcript(transcript):
    return re.sub(r"\s+", " ", re.sub(r"\[.*?\]", "", transcript)).strip()

# Extract video ID from YouTube URL
def extract_video_id(video_url):
    try:
        query = urllib.parse.urlparse(video_url).query
        video_id = urllib.parse.parse_qs(query).get("v", [None])[0]
        if not video_id:
            raise ValueError("Invalid YouTube URL")
        return video_id
    except Exception as e:
        logging.error(f"Error parsing video ID: {e}")
        raise ValueError("Invalid YouTube URL format.")

# Fetch transcript from YouTube
def get_transcript(video_url):
    try:
        video_id = extract_video_id(video_url)
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return clean_transcript(" ".join([entry["text"] for entry in transcript]))
    except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable) as e:
        return f"Error: {str(e)}"
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return f"Error: {str(e)}"

# Split text into chunks for summarization
def split_into_chunks(text, max_length=1024):
    words, chunks, current_chunk = text.split(), [], []
    current_length = 0
    for word in words:
        if current_length + len(word) + 1 > max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk, current_length = [], 0
        current_chunk.append(word)
        current_length += len(word) + 1
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

# Summarize text using BART
def summarize_text(text):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn", framework="pt")
    chunks = split_into_chunks(text)
    return " ".join(
        summarizer(chunk, max_length=150, min_length=50, do_sample=False)[0]["summary_text"]
        for chunk in chunks
    )

# Endpoint to process YouTube videos
@app.route("/process", methods=["POST"])
def process_video():
    try:
        data = request.json
        youtube_url = data.get("youtube_url", None)
        if not youtube_url:
            return jsonify({"error": "YouTube URL is required"}), 400

        transcript = get_transcript(youtube_url)
        if transcript.startswith("Error"):
            return jsonify({"error": transcript}), 400

        summary = summarize_text(transcript)
        return jsonify({"summary": summary}), 200
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True)
