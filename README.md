
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
![App Screenshot](https://github.com/gunjanBabu29/YT-Video-Script-Summarizer-/blob/main/img.jpg)  
![App Screenshot](https://github.com/gunjanBabu29/YT-Video-Script-Summarizer-/blob/main/img1.jpg)
 

## Installation  

1. Clone this repository:  
   ```bash  
   git clone https://github.com/gunjanBabu29/YT-Video-Script-Summarizer-.git  
   ```  

2. Navigate to the project directory:  
   ```bash  
   cd YT-Video-Script-Summarizer-  
   ```  

3. Create a virtual environment and activate it:  
   ```bash  
   python -m venv venv  
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`  
   ```  

4. Install dependencies:  
   ```bash  
   pip install -r requirements.txt  
   ```  

5. Create a `.env` file in the project root and add the following:  
   ```env  
   GOOGLE_API_KEY=your_google_api_key  
   YOUTUBE_API_KEY=your_youtube_api_key  
   ```  

6. Run the application:  
   ```bash  
   streamlit run app.py  
   ```  

## Usage  

1. Enter the YouTube video URL in the input field.  
2. The app will display the video thumbnail, title, channel name, views, and likes on the left panel.  
3. Click the **Get Detailed Notes** button to generate summaries in English and Hindi.  
4. Summaries will be displayed in the right panel.  

## Technologies Used  
- **Python**  
- **Streamlit**  
- **YouTube Data API**  
- **Google Generative AI API**  

## API Keys Setup  

- To use this application, you need to obtain API keys for:  
  1. **YouTube Data API**: [Get the key here](https://console.cloud.google.com/)  
  2. **Google Generative AI API**: [Get the key here](https://console.cloud.google.com/)  

Add the keys in the `.env` file as described above.  

## Deployment  

This app is deployed on Streamlit Cloud. You can access it at:  
[https://yt-video-scripter.streamlit.app/](https://yt-video-scripter.streamlit.app/)  

## Contribution Guidelines  

Contributions are welcome!  

1. Fork the repository:  
   ```bash  
   git fork https://github.com/gunjanBabu29/YT-Video-Script-Summarizer-.git  
   ```  

2. Clone your forked repository locally:  
   ```bash  
   git clone https://github.com/your_username/YT-Video-Script-Summarizer-.git  
   ```  

3. Create a new branch:  
   ```bash  
   git checkout -b feature-name  
   ```  

4. Make changes, test them locally, and commit:  
   ```bash  
   git commit -m "Added feature-name"  
   ```  

5. Push changes to your forked repository:  
   ```bash  
   git push origin feature-name  
   ```  

6. Open a pull request against the original repository.  

## License  

This project is licensed under the MIT License. See the LICENSE file for details.  

```plaintext  
MIT License  

Copyright (c) 2024 Gunjan Kumar  

Permission is hereby granted, free of charge, to any person obtaining a copy  
of this software and associated documentation files (the "Software"), to deal  
in the Software without restriction, including without limitation the rights  
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell  
copies of the Software, and to permit persons to whom the Software is  
furnished to do so, subject to the following conditions:  

The above copyright notice and this permission notice shall be included in all  
copies or substantial portions of the Software.  

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,  
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,  
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE  
SOFTWARE.  
```  

## Author  

- **Gunjan Kumar**  
  GitHub: [gunjanBabu29](https://github.com/gunjanBabu29)  

---  

Happy Summarizing! 🚀
