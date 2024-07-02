from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables
load_dotenv()

# Configure Google Gemini Pro
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Flask app setup
app = Flask(__name__)

# Enhanced prompt for summary
prompt = """
You are a YouTube video summarizer. Your task is to summarize the entire video by extracting key points, main ideas, and important details in a concise manner. Ensure the summary is well-structured and within 500 words. Please organize the summary as follows:

1. Introduction: Briefly describe the video's topic and purpose.
2. Key Points: List the main points discussed in the video.
3. Important Details: Highlight any significant details or examples provided.
4. Conclusion: Summarize the overall message or takeaway from the video.

Please provide the summary of the text given here: """

def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("v=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([item["text"] for item in transcript_text])
        return transcript
    except Exception as e:
        return str(e)

def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_notes', methods=['POST'])
def get_notes():
    youtube_link = request.form['youtube_link']
    transcript_text = extract_transcript_details(youtube_link)
    if transcript_text:
        summary = generate_gemini_content(transcript_text, prompt)
        return jsonify({'summary': summary, 'video_id': youtube_link.split('v=')[1]})
    else:
        return jsonify({'error': 'Unable to fetch transcript'})

if __name__ == '__main__':
    app.run(debug=True)

