from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from transformers import pipeline
from flask_cors import CORS
from waitress import serve
import requests
import re
import urllib.parse

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Nhost configuration
NHOST_GRAPHQL_URL = "https://pcpbxvkqnfgbyqbsydgy.hasura.ap-south-1.nhost.run/v1/graphql"
NHOST_ADMIN_SECRET = "q)OT'V-#ZA9P2m1%qt&R#dMI+YpE8loh"

# Helper function to clean transcript
def clean_transcript(transcript):
    cleaned = re.sub(r"\[.*?\]", "", transcript)  # Remove text in brackets like [music]
    return re.sub(r"\s+", " ", cleaned).strip()  # Remove excessive spaces or newlines

# Function to extract video ID from YouTube URL
def extract_video_id(video_url):
    try:
        query = urllib.parse.urlparse(video_url).query
        video_id = urllib.parse.parse_qs(query).get("v", [None])[0]
        if not video_id:
            raise ValueError("Invalid YouTube URL")
        return video_id
    except Exception as e:
        raise ValueError(f"Error parsing video ID: {str(e)}")

# Function to get transcript
def get_transcript(video_url):
    try:
        video_id = extract_video_id(video_url)
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        raw_text = " ".join([entry["text"] for entry in transcript])
        return clean_transcript(raw_text)
    except TranscriptsDisabled:
        return "Error: Subtitles are disabled for this video."
    except NoTranscriptFound:
        return "Error: No transcript found for this video."
    except VideoUnavailable:
        return "Error: This video is unavailable."
    except Exception as e:
        return f"Error: {str(e)}"

# Function to split text into chunks for summarization
def split_into_chunks(text, max_length=1024):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    for word in words:
        if current_length + len(word) + 1 > max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0
        current_chunk.append(word)
        current_length += len(word) + 1
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

# Function to summarize text
def summarize_text(text):
    try:
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn", framework="pt")
        chunks = split_into_chunks(text)
        summaries = [summarizer(chunk, max_length=150, min_length=50, do_sample=False)[0]["summary_text"] for chunk in chunks]
        return " ".join(summaries)
    except PipelineException as e:
        return f"Error during summarization: {str(e)}"
    except Exception as e:
        return f"Error during summarization: {str(e)}"

# Endpoint to process video
@app.route("/process", methods=["POST"])
def process_video():
    data = request.json
    youtube_url = data.get("youtube_url")
    if not youtube_url:
        return jsonify({"error": "YouTube URL is required"}), 400

    # Get transcript
    transcript = get_transcript(youtube_url)
    if transcript.startswith("Error"):
        return jsonify({"error": transcript}), 400

    # Summarize transcript
    summary = summarize_text(transcript)
    if summary.startswith("Error"):
        return jsonify({"error": summary}), 500

    # Save to Nhost
    graphql_query = """
    mutation InsertSummary($youtube_url: String!, $summary: String!) {
        insert_video_summaries(objects: {youtube_url: $youtube_url, summary: $summary}) {
            affected_rows
        }
    }
    """
    headers = {
        "Content-Type": "application/json",
        "x-hasura-admin-secret": NHOST_ADMIN_SECRET
    }
    variables = {
        "youtube_url": youtube_url,
        "summary": summary
    }

    response = requests.post(NHOST_GRAPHQL_URL, json={"query": graphql_query, "variables": variables}, headers=headers)
    if response.status_code == 200:
        return jsonify({"message": "Processed successfully!", "summary": summary}), 200
    else:
        return jsonify({"error": "Failed to save to database"}), 500

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5000)
