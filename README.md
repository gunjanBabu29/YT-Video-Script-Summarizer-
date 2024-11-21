# YouTube Video Script Summarizer  

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_red.svg)](https://yt-video-scripter.streamlit.app/)  

A Streamlit-based web application that extracts and summarizes YouTube video scripts in both English and Hindi.  

## Features  
- Extracts transcripts from YouTube videos (if available).  
- Summarizes video content into concise notes in English and Hindi.  
- Displays video details, including title, channel name, views, likes, and thumbnail.  
- Simple and responsive user interface for better usability.  

## Demo  
Check out the live application [here](https://yt-video-scripter.streamlit.app/).  

## Screenshots  
![App Screenshot](https://via.placeholder.com/1200x600?text=Screenshot+Placeholder)  
*Replace this placeholder with your actual screenshot.*  

## Installation  

1. Clone this repository:  
   ```bash  
   git clone https://github.com/gunjanBabu29/YT-Video-Script-Summarizer-.git  
Navigate to the project directory:

bash
Copy code
cd YT-Video-Script-Summarizer-  
Create a virtual environment and activate it:

 bash
Copy code
python -m venv venv  
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`  
Install dependencies:

bash
Copy code
pip install -r requirements.txt  
Create a .env file in the project root and add the following:

env
Copy code
GOOGLE_API_KEY=your_google_api_key  
YOUTUBE_API_KEY=your_youtube_api_key  
Run the application:

bash
Copy code
streamlit run app.py  
Usage
Enter the YouTube video URL in the input field.
The app will display the video thumbnail, title, channel name, views, and likes on the left panel.
Click the Get Detailed Notes button to generate summaries in English and Hindi.
Summaries will be displayed in the right panel.
Technologies Used
Python
Streamlit
YouTube Data API
Google Generative AI API
API Keys Setup
To use this application, you need to obtain API keys for:
YouTube Data API: Get the key here
Google Generative AI API: Get the key here
Add the keys in the .env file as described above.

Deployment
This app is deployed on Streamlit Cloud. You can access it at:
https://yt-video-scripter.streamlit.app/

Contributing
Contributions are welcome!

Fork the repository.
Create a new branch:
bash
Copy code
git checkout -b feature-name  
Make your changes and commit:
bash
Copy code
git commit -m "Added feature-name"  
Push to the branch:
bash
Copy code
git push origin feature-name  
Submit a pull request.
License
This project is open-source and available under the MIT License.

Author
Gunjan Kumar
GitHub: gunjanBabu29
Happy Summarizing! 🚀

vbnet
Copy code

Feel free to modify the placeholders (e.g., screenshots or additional info) as needed!
