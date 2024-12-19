import streamlit as st
from dotenv import load_dotenv
import os
from urllib.parse import urlparse, parse_qs
import google.generativeai as genai 
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Google API Key for YouTube Data API
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Prompts for Gemini
english_prompt = """You are a YouTube video summarizer.~ Summarize the transcript text
and provide the most important points in English within 250 words."""

hindi_prompt = """Aap ek YouTube video summary creator hain. Transcript text ka summary 
tayar karein aur 250 shabdon ke andar Hindi mein sabse important points provide karein"""

# Inject custom CSS
def add_custom_css():
    st.markdown(
        """
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background-color: #f5f5f5;
                margin: 0;
                padding: 0;
            }
            .css-1y4p8pa {
                background-color: #ffffff !important;
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            }
            h1 {
                text-align: center;
                background: linear-gradient(90deg, red, orange, yellow, green, blue, indigo, violet);
                -webkit-background-clip: text;
                color: transparent;
                margin-bottom: 20px;
            }
            .rainbow-divider {
                height: 5px;
                color: red;
                background: linear-gradient(90deg, red, orange, yellow, green, blue, indigo, violet);
                border: none;
                margin: 10px 0 20px 0;
            }
            .info-line {
                display: flex;
                justify-content: space-between;
                font-size: 16px;
                margin: 10px 0;
                padding: 10px;
                background-color: #f9f9f9;
                border-radius: 10px;
                border: 1px solid #ddd;
            }
            .info-line div {
                flex: 1;
                text-align: center;
                color: #2c3e50;
                font-weight: bold;
            }
            .summary-section {
                margin: 20px 0;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 10px;
                background-color: #fff;
            }
            .summary-section h2 {
                color: #16A085;
            }
            .button-container a button {
                background-color: #3498DB;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
                cursor: pointer;
                margin-top: 20px;
                border-radius: 5px;
                transition: 0.3s;
            }
            .button-container a button:hover {
                background-color: #2E86C1;
            }
            .footer {
                text-align: center;
                margin-top: 50px;
                padding: 10px;
                font-size: 14px;
                color: #555;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Function to extract video ID from URL
def get_video_id(youtube_url):
    parsed_url = urlparse(youtube_url)
    if parsed_url.netloc in ["www.youtube.com", "youtube.com"]:
        return parse_qs(parsed_url.query).get("v", [None])[0]
    elif parsed_url.netloc in ["youtu.be"]:
        return parsed_url.path[1:]
    return None

# Function to extract video details
def get_video_details(video_id):
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        request = youtube.videos().list(part="snippet,statistics", id=video_id)
        response = request.execute()

        if "items" in response and len(response["items"]) > 0:
            snippet = response["items"][0]["snippet"]
            channel_id = snippet["channelId"]
            channel_name = snippet["channelTitle"]
            statistics = response["items"][0]["statistics"]
            views = "{:,}".format(int(statistics.get("viewCount", 0)))
            likes = "{:,}".format(int(statistics.get("likeCount", 0))) if "likeCount" in statistics else "N/A"

            # Fetching subscriber count from channel details
            channel_request = youtube.channels().list(part="statistics", id=channel_id)
            channel_response = channel_request.execute()
            if "items" in channel_response and len(channel_response["items"]) > 0:
                subscriber_count = channel_response["items"][0]["statistics"].get("subscriberCount", "N/A")
                if subscriber_count != "N/A":
                    subscriber_count = "{:,}".format(int(subscriber_count))
            else:
                subscriber_count = "N/A"

            return channel_name, views, subscriber_count, likes
        else:
            return "Channel information unavailable", "0", "N/A", "N/A"

    except Exception as e:
        return f"Error fetching video details: {str(e)}", "0", "N/A", "N/A"

# Function to fetch transcript with fallback
def fetch_transcript(youtube_video_url):
    video_id = get_video_id(youtube_video_url)
    if not video_id:
        return None, "Invalid YouTube URL. Please check the link and try again."

    # Try to fetch transcript using YouTubeTranscriptApi
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=["hi", "en"])
        transcript = " ".join([item["text"] for item in transcript_data])
        return transcript, None
    except (TranscriptsDisabled, NoTranscriptFound):
        # If no transcript is found, fallback to YouTube API captions
        transcript, error = fetch_captions_with_youtube_api(video_id)
        if error:
            return None, error
        else:
            return transcript, None
    except Exception as e:
        return None, f"An error occurred: {str(e)}"

# Fallback function to fetch captions from YouTube API
def fetch_captions_with_youtube_api(video_id):
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        request = youtube.captions().list(part="snippet", videoId=video_id)
        response = request.execute()
        if response["items"]:
            return "Captions found", None
        else:
            return None, "No captions available for this video."
    except Exception as e:
        return None, f"Error fetching captions: {str(e)}"

# Function to generate content using Gemini
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Streamlit app interface
add_custom_css()
st.markdown(
    """
    <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 20px;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/4/42/YouTube_icon_%282013-2017%29.png" alt="YouTube Logo" width="40" style="margin-right: 10px;">
        <h1>YouTube Transcript Summarizer</h1>
    </div>
    <hr class="rainbow-divider">
    """,
    unsafe_allow_html=True,
)

youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = get_video_id(youtube_link)
    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)

        # Display video details in a single aligned row
        channel_name, views, subscribers, likes = get_video_details(video_id)
        st.markdown(
            f"""
            <div class="info-line">
                <div>Channel: {channel_name}</div>
                <div>Views: {views}</div>
                <div>Subscribers: {subscribers}</div>
                <div>Likes: {likes}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

if st.button("Get Detailed Notes"):
    transcript_text, error = fetch_transcript(youtube_link)

    if error:
        st.error(error)
    else:
        # Generate English summary
        english_summary = generate_gemini_content(transcript_text, english_prompt)
        st.markdown("<div class='summary-section'><h2>Detailed Summary 📝:-</h2>", unsafe_allow_html=True)
        st.write(english_summary)

        # Generate Hindi summary
        hindi_summary = generate_gemini_content(transcript_text, hindi_prompt)
        st.markdown("<h2>Summary in Hindi:</h2></div>", unsafe_allow_html=True)
        st.write(hindi_summary)

        # Add a button to redirect to the YouTube video
        st.markdown(
            f"""
            <div class="button-container">
                <a href="{youtube_link}" target="_blank">
                    <button>Click Here to Directly Visit the YouTube Video</button>
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Footer
st.markdown(
    """
    <div class="footer">
        &copy; 2024 | Made with ❤️ by Gunjan Kumar
    </div>
    """,
    unsafe_allow_html=True,
)
