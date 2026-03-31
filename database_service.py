import os
import random
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client
from yt_dlp import YoutubeDL

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- CONFIGURATION ---
TRUSTED_CHANNELS = [
    "https://www.youtube.com/@MadFit/videos",
    "https://www.youtube.com/@CHRISHERIA/videos",
    "https://www.youtube.com/@Growingannanas/videos",
    "https://www.youtube.com/@BullyJuice/videos"
]

@st.cache_data(ttl=300)
def get_all_workouts():
    response = supabase.table("workouts").select("*").order("created_at", desc=True).execute()
    return response.data

def get_workout_today():
    response = supabase.table("workout_today").select("*, workouts(*)").eq("id", 1).execute()
    return response.data

def update_workout_today(video_id):
    supabase.table("workout_today").upsert({"id": 1, "video_id": video_id}).execute()

def add_workout_by_url(url):
    ydl_opts = {'quiet': True, 'no_warnings': True}
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            data = {
                "video_id": info.get("id"),
                "title": info.get("title"),
                "url": url,
                "channel": info.get("uploader"),
                "duration_seconds": info.get("duration")
            }
            supabase.table("workouts").upsert(data).execute()
            update_workout_today(data["video_id"])
            st.cache_data.clear()
            return True
    except Exception as e:
        return False

def discover_new_workout():
    """Scrapes a random video from trusted YouTube channels."""
    channel_url = random.choice(TRUSTED_CHANNELS)
    # We only want the metadata, not the video file
    ydl_opts = {'quiet': True, 'extract_flat': True, 'force_generic_extractor': True}
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            channel_info = ydl.extract_info(channel_url, download=False)
            videos = channel_info.get('entries', [])
            if not videos: return None
            
            # Pick a random one from the 15 most recent uploads
            selected = random.choice(videos[:15])
            video_url = f"https://www.youtube.com/watch?v={selected['id']}"
            
            # Add to DB and set as Active
            add_workout_by_url(video_url)
            return video_url
    except Exception as e:
        st.error(f"Discovery Error: {e}")
        return None

def delete_workout(video_id):
    # SQL Cascade handles the workout_today link automatically now!
    supabase.table("workouts").delete().eq("video_id", video_id).execute()
    st.cache_data.clear()
    return True

# --- NEW: PROGRESS TRACKER LOGIC ---
def log_completed_workout(video_id):
    """Logs a completion for the tracker."""
    supabase.table("progress").insert({"video_id": video_id}).execute()

def get_weekly_progress():
    """Fetches count of workouts in the last 7 days."""
    # Simplified for now: just returns total count
    response = supabase.table("progress").select("*").execute()
    return len(response.data)