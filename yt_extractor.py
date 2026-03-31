import os
import streamlit as st
import yt_dlp
from dotenv import load_dotenv

# 1. SETUP: Load local .env (for your laptop)
load_dotenv()

# 2. CLOUD-AWARE KEY: This looks in Streamlit Secrets first, then your .env
YOUTUBE_API_KEY = st.secrets.get("YOUTUBE_API_KEY") or os.getenv("YOUTUBE_API_KEY")

# Safety check: Stop the app if the key is missing in the cloud
if not YOUTUBE_API_KEY:
    # We only show this error if we are in the Streamlit app context
    try:
        st.error("YouTube API Key is missing! Add it to your Streamlit Secrets.")
    except:
        print("Warning: YOUTUBE_API_KEY not found in environment.")

def get_video_metadata(url):
    """
    Extracts the Title, Channel, and Duration from a YouTube URL.
    This is the engine that fills your database automatically!
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # We fetch the info without downloading the actual video
            info = ydl.extract_info(url, download=False)
            
            return {
                "video_id": info.get("id"),
                "title": info.get("title"),
                "channel": info.get("uploader"),
                "duration_seconds": info.get("duration"),
                "url": url
            }
    except Exception as e:
        # Log error to terminal
        print(f"Error extracting metadata: {e}")
        return None

# --- TEST BLOCK ---
if __name__ == "__main__":
    # Test with a sample workout video
    test_url = "https://www.youtube.com/watch?v=KMkmA4i2FQc"
    print("Extracting info...")
    data = get_video_metadata(test_url)
    
    if data:
        print(f"Success! Found: {data['title']} by {data['channel']}")
        print(f"Duration: {data['duration_seconds']} seconds")