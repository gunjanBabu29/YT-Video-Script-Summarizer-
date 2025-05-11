import streamlit as st
from dotenv import load_dotenv
import os
from urllib.parse import urlparse, parse_qs, quote
import google.generativeai as genai 
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from googleapiclient.discovery import build
import random  # For random facts
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Google API Key for YouTube Data API
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Proxy setup from .env
http_proxy = os.getenv("HTTP_PROXY")
https_proxy = os.getenv("HTTPS_PROXY")

# List of motivational facts
MOTIVATIONAL_FACTS = [
    "Stay hungry, stay foolish. – Steve Jobs",
    "Do what you can, with what you have. – Theodore Roosevelt",
    "Success is not final, failure is not fatal. – Winston Churchill",
    "Injustice anywhere is a threat to justice everywhere. – Martin Luther King Jr.",
    "The only limit to our realization of tomorrow is doubt. – Franklin D. Roosevelt",
    "Happiness depends upon ourselves. – Aristotle",
    "Turn your wounds into wisdom. – Oprah Winfrey",
    "Life is either a daring adventure or nothing. – Helen Keller",
    "Simplicity is the ultimate sophistication. – Leonardo da Vinci",
    "It always seems impossible until it’s done. – Nelson Mandela"
]

# Function to extract video ID from URL
def get_video_id(youtube_url):
    parsed_url = urlparse(youtube_url)
    if parsed_url.netloc in ["www.youtube.com", "youtube.com"]:
        return parse_qs(parsed_url.query).get("v", [None])[0]
    elif parsed_url.netloc in ["youtu.be"]:
        return parsed_url.path[1:]
    return None

# Function to create social media share links
def create_share_links(video_url, summary_text=None):
    encoded_url = quote(video_url)
    encoded_summary = quote(summary_text) if summary_text else ""
    
    # Twitter share link
    twitter_link = f"https://twitter.com/intent/tweet?url={encoded_url}&text={encoded_summary}"
    
    # Facebook share link
    facebook_link = f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}"
    
    # LinkedIn share link
    linkedin_link = f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}"
    
    return {
        "Twitter": twitter_link,
        "Facebook": facebook_link,
        "LinkedIn": linkedin_link,
    }
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

    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(
            video_id,
            languages=["en", "hi"],
            proxies=proxies
        )
        transcript = " ".join([item["text"] for item in transcript_data])
        return transcript, None
    except (TranscriptsDisabled, NoTranscriptFound):
        return None, "Transcript is disabled or not available for this video."
    except Exception as e:
        return None, f"An error occurred while fetching the transcript: {str(e)}"


# Function to preprocess transcript to avoid triggering safety filters
def preprocess_transcript(transcript_text):
    # Remove potentially harmful keywords or phrases
    harmful_keywords = ["sexually explicit", "hate speech", "harassment", "dangerous content"]
    for keyword in harmful_keywords:
        transcript_text = transcript_text.replace(keyword, "[REDACTED]")
    return transcript_text

# Function to generate content using Gemini
def generate_gemini_content(transcript_text, prompt, max_words):
    model = genai.GenerativeModel("gemini-1.5-flash")
    # Configure safety settings to allow more flexibility
    safety_settings = {
        "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
        "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
        "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
        "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
    }
    try:
        # Preprocess transcript to avoid triggering safety filters
        transcript_text = preprocess_transcript(transcript_text)
        
        # Truncate transcript to avoid exceeding token limits
        MAX_TOKENS = 30000  # Gemini Pro's token limit
        truncated_transcript = transcript_text[:MAX_TOKENS]
        
        # Ensure all parts of the prompt are strings
        full_prompt = str(prompt) + " " + str(truncated_transcript) + f" Limit the summary to {max_words} words."
        
        # Generate content with retry logic
        retries = 3
        for attempt in range(retries):
            try:
                response = model.generate_content(full_prompt, safety_settings=safety_settings)
                if response.candidates:
                    return response.text
                else:
                    return "Unable to generate summary due to content restrictions."
            except Exception as e:
                if attempt == retries - 1:  # Last attempt
                    return f"An error occurred after {retries} attempts: {str(e)}"
                continue
    except Exception as e:
        return f"An error occurred while generating the summary: {str(e)}"
    
st.markdown(
    """
<link rel="stylesheet" href="styles.css">
""",
 unsafe_allow_html=True,

)


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
                color: #FFFFFF;
                background-color: #4CAF50;
                padding: 20px;
                border-radius: 10px 10px 0 0;
                margin: 0;
                font-size: 2.5rem;
                font-weight: bold;
            }
            .header-border {
                border-bottom: 5px solid #c64adf;
                margin-top: 0;
            }
            .rainbow-divider {
                height: 5px;
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
                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            }
            .summary-section h2 {
                color: #16A085;
                font-size: 1.5rem;
                margin-bottom: 10px;
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
            iframe {
                margin: 20px auto;
                display: block;
                border-radius: 10px;
                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            }
            
        </style>
        """,
        unsafe_allow_html=True,
    )

# Streamlit app interface
add_custom_css()

# Sidebar for sharing links
st.sidebar.title("Enter YT Video Link")
# st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/4/42/YouTube_icon_%282013-2017%29.png", width=50)
youtube_link = st.sidebar.text_input("Paste Your Link here:")

# Add spacing and buttons with alignment
col1, col2, col3 = st.sidebar.columns([1.3, 1, 1])  # Adjust the first value (0.2) to control the left padding
with col2:
    if st.button("Clear", help="Clear the input field", key="clear_button"):
        youtube_link = ""
        st.session_state.youtube_link = "" 
        # st.experimental_rerun()

with col3:
    if st.button("Submit", help="Proceed with the entered link", key="submit_button"):
        pass  # Proceed with the existing logic

# Main app interface
st.markdown(
    """
    <div>
        <h1>▶️YouTube Transcript Summarizer</h1>
        <div class="header-border"></div>
        <p style="text-align: center; font-size: 1.2rem; color: #555; margin-top: 10px;">
            Summarize, Analyze, and Download Notes from Any YouTube Video!
        </p>
    </div>
    <hr class="rainbow-divider">
    """,
    unsafe_allow_html=True,
)

if youtube_link:
    video_id = get_video_id(youtube_link)
    if video_id:
        # Display embedded YouTube video
        st.markdown(
            f"""
            <div style="text-align: center; margin-bottom: 20px;">
                <iframe width="560" height="315" 
                        src="https://www.youtube.com/embed/{video_id}" 
                        frameborder="0" 
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                        allowfullscreen>
                </iframe>
            </div>
            """,
            unsafe_allow_html=True,
        )
  
        
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

        # Word count dropdown
        max_words = st.selectbox("Select Summary Length (in words):", [100, 200, 300, 400, 500])

        if st.button("Get Detailed Notes 📝"):
            # Show a random motivational fact while processing
            random_fact = random.choice(MOTIVATIONAL_FACTS)
            with st.spinner(f"Processing... Fact: {random_fact}"):
                transcript_text, error = fetch_transcript(youtube_link)
                if error:
                    st.error(error)
                else:
                    # Generate English summary
                    english_summary = generate_gemini_content(transcript_text, """You are a YouTube video summarizer. Your task is to summarize the provided transcript text, 
highlighting the key points in bullet format within 500 words. Please provide the summary of the text: 
- Introduction: The video introduces the main topic, explaining its relevance and setting the stage for the discussion.
- Key Point 1: The first major point, detailing important aspects and their implications.
- Key Point 2: The second key topic, providing relevant findings, examples, and insights.
- Key Point 3: Another critical topic discussed, highlighting key examples and their broader impact.
- Supporting Points: Additional topics that reinforce the main discussion and provide supporting evidence.
- Expert Opinion: Insights or recommendations from the speaker, adding depth and perspective.
- Conclusion: A wrap-up of the main takeaways, with a final call to action or thought for the viewer.""", max_words)
                    st.markdown("<div class='summary-section'><h2>Detailed Summary 📝:</h2>", unsafe_allow_html=True)
                    st.write(english_summary)

                    # Generate Hindi summary
                    hindi_summary = generate_gemini_content(transcript_text, """Aap ek YouTube video summary creator hain. Transcript text ka summary 
tayar karein aur 500 shabdon ke andar Hindi mein sabse important points provide karein.
                                                            - Introduction
                                                            -MAIN pOINT
                                                            - cONCLUSION""", max_words)
                    st.markdown("<h2>Summary in Hindi:</h2></div>", unsafe_allow_html=True)
                    st.write(hindi_summary)

                    # Download summaries as TXT
                    txt_filename = "summaries.txt"
                    with open(txt_filename, "w", encoding="utf-8") as file:
                        file.write("# English Summary\n")
                        file.write(english_summary + "\n\n")
                        file.write("# Hindi Summary\n")
                        file.write(hindi_summary + "\n")
                    
                    # Add download button without reloading the page
                    with open(txt_filename, "rb") as file:
                        st.download_button(
                            label="Download Summaries as TXT 📥",
                            data=file,
                            file_name=txt_filename,
                            mime="text/plain",
                            key="download_button"  # Add a unique key to prevent reload issues
                        )
                    # Add social media sharing buttons with icons
                    st.markdown("### Share on:")
                    share_links = create_share_links(youtube_link, english_summary)
                    
                    # Use Font Awesome icons for social media
                    st.markdown("""
                        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
                        <div style="display: flex; gap: 10px;">
                            <a href="{twitter_link}" target="_blank" title="Share on Twitter">
                                <i class="fab fa-twitter" style="font-size: 24px; color: #1DA1F2;"></i>
                            </a>
                            <a href="{facebook_link}" target="_blank" title="Share on Facebook">
                                <i class="fab fa-facebook" style="font-size: 24px; color: #1877F2;"></i>
                            </a>
                            <a href="{linkedin_link}" target="_blank" title="Share on LinkedIn">
                                <i class="fab fa-linkedin" style="font-size: 24px; color: #0A66C2;"></i>
                            </a>
                        </div>
                    """.format(
                        twitter_link=share_links["Twitter"],
                        facebook_link=share_links["Facebook"],
                        linkedin_link=share_links["LinkedIn"]
                    ), unsafe_allow_html=True)

# Footer
st.markdown(
    """
    <div class="footer">
        &copy; 2024 | Made with ❤️ by Gunjan Kumar |
    </div>
    """,
    unsafe_allow_html=True,
)
