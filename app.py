import streamlit as st
from dotenv import load_dotenv
import os
from urllib.parse import urlparse, parse_qs
import google.generativeai as genai 
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.proxies import Proxies
import random  # For random facts
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use proxy from .env if available
http_proxy = os.getenv("HTTP_PROXY")
https_proxy = os.getenv("HTTPS_PROXY")

proxies = {
    "http": http_proxy,
    "https": https_proxy
} if http_proxy and https_proxy else None

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
    encoded_url = video_url.replace("https://", "").replace("http://", "")
    encoded_summary = summary_text[:200] + "..." if summary_text and len(summary_text) > 200 else summary_text
    twitter_link = f"https://twitter.com/intent/tweet?url= {encoded_url}&text={encoded_summary}"
    facebook_link = f"https://www.facebook.com/sharer/sharer.php?u= {video_url}"
    linkedin_link = f"https://www.linkedin.com/sharing/share-offsite/?url= {video_url}"
    return {"Twitter": twitter_link, "Facebook": facebook_link, "LinkedIn": linkedin_link}

# Function to fetch transcript with retry logic and proxy support
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
    harmful_keywords = ["sexually explicit", "hate speech", "harassment", "dangerous content"]
    for keyword in harmful_keywords:
        transcript_text = transcript_text.replace(keyword, "[REDACTED]")
    return transcript_text

# Function to generate content using Gemini
def generate_gemini_content(transcript_text, prompt, max_words):
    model = genai.GenerativeModel("gemini-1.5-flash")  # Changed to Flash for better rate limits
    safety_settings = {
        "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
        "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
        "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
        "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
    }
    try:
        transcript_text = preprocess_transcript(transcript_text)
        MAX_TOKENS = 30000
        truncated_transcript = transcript_text[:MAX_TOKENS]
        full_prompt = str(prompt) + " " + str(truncated_transcript) + f" Limit the summary to {max_words} words."
        retries = 3
        for attempt in range(retries):
            try:
                response = model.generate_content(full_prompt, safety_settings=safety_settings)
                if response.candidates:
                    return response.text
                else:
                    return "Unable to generate summary due to content restrictions."
            except Exception as e:
                if "429" in str(e):
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    return f"An error occurred: {str(e)}"
    except Exception as e:
        return f"An error occurred while generating the summary: {str(e)}"

# Motivational Facts
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

# UI Section
st.markdown(
    """
    <link rel="stylesheet" href="styles.css">
    """,
    unsafe_allow_html=True,
)

# Sidebar
st.sidebar.title("Enter YT Video Link")
youtube_link = st.sidebar.text_input("Paste Your Link here:")

col1, col2, col3 = st.sidebar.columns([1.3, 1, 1])
with col2:
    if st.button("Clear", help="Clear the input field", key="clear_button"):
        youtube_link = ""
with col3:
    submit = st.button("Submit", help="Proceed with the entered link", key="submit_button")

# Main UI
st.markdown(
    """
    <div>
        <h1>▶️YouTube Transcript Summarizer</h1>
        <p style="text-align: center; font-size: 1.2rem; color: #555;">
            Summarize, Analyze, and Download Notes from Any YouTube Video!
        </p>
    </div>
    <hr class="rainbow-divider">
    """,
    unsafe_allow_html=True,
)

if submit and youtube_link:
    video_id = get_video_id(youtube_link)
    if video_id:
        st.markdown(
            f"""
            <iframe width="560" height="315" src="https://www.youtube.com/embed/ {video_id}" frameborder="0" allowfullscreen></iframe>
            """,
            unsafe_allow_html=True,
        )

        max_words = st.selectbox("Select Summary Length (in words):", [100, 200, 300, 400, 500])

        if st.button("Get Detailed Notes 📝"):
            random_fact = random.choice(MOTIVATIONAL_FACTS)
            with st.spinner(f"Processing... Fact: {random_fact}"):
                transcript_text, error = fetch_transcript(youtube_link)
                if error:
                    st.error(error)
                else:
                    # Generate English Summary
                    english_summary = generate_gemini_content(transcript_text, """You are a YouTube video summarizer. Your task is to summarize the provided transcript text, highlighting the key points in bullet format within 500 words. Please provide the summary of the text: 
                        - Introduction
                        - Key Points
                        - Supporting Details
                        - Expert Opinion
                        - Conclusion""", max_words)

                    st.markdown("<div class='summary-section'><h2>Detailed Summary 📝:</h2>", unsafe_allow_html=True)
                    st.write(english_summary)

                    # Generate Hindi Summary
                    hindi_summary = generate_gemini_content(transcript_text, """Aap ek YouTube video summary creator hain. Transcript text ka summary tayar karein aur 500 shabdon ke andar sabse important points provide karein.
                        - Introduction
                        - MAIN pOINT
                        - cONCLUSION""", max_words)

                    st.markdown("<h2>Summary in Hindi:</h2></div>", unsafe_allow_html=True)
                    st.write(hindi_summary)

                    # Save and download summaries
                    txt_filename = "summaries.txt"
                    with open(txt_filename, "w", encoding="utf-8") as file:
                        file.write("# English Summary\n")
                        file.write(english_summary + "\n\n")
                        file.write("# Hindi Summary\n")
                        file.write(hindi_summary + "\n")

                    with open(txt_filename, "rb") as file:
                        st.download_button(
                            label="Download Summaries as TXT 📥",
                            data=file,
                            file_name=txt_filename,
                            mime="text/plain",
                            key="download_button"
                        )

                    # Social sharing
                    st.markdown("### Share on:")
                    share_links = create_share_links(youtube_link, english_summary)
                    st.markdown("""
                        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css ">
                        <div style="display: flex; gap: 10px;">
                            <a href="{twitter_link}" target="_blank"><i class="fab fa-twitter" style="font-size: 24px; color: #1DA1F2;"></i></a>
                            <a href="{facebook_link}" target="_blank"><i class="fab fa-facebook" style="font-size: 24px; color: #1877F2;"></i></a>
                            <a href="{linkedin_link}" target="_blank"><i class="fab fa-linkedin" style="font-size: 24px; color: #0A66C2;"></i></a>
                        </div>
                    """.format(**share_links), unsafe_allow_html=True)

# Footer
st.markdown(
    """
    <div class="footer">
        © 2024 | Made with ❤️ by Gunjan Kumar |
    </div>
    """,
    unsafe_allow_html=True,
)
