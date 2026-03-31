import os
import random
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timedelta

# 1. SETUP: Load keys from .env (Local) or st.secrets (Cloud)
load_dotenv()

# This logic checks BOTH places automatically
SUPABASE_URL = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")

# Stop the app if keys are missing to prevent a crash
if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Missing Supabase Credentials! Please check your .env file or Streamlit Secrets.")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- DATABASE OPERATIONS ---

def add_workout(video_id, title, url, channel=None, duration=None):
    """Adds a workout to the main library."""
    data = {
        "video_id": video_id,
        "title": title,
        "url": url,
        "channel": channel,
        "duration_seconds": duration
    }
    return supabase.table("workouts").upsert(data).execute()

def get_all_workouts():
    """Fetches all workouts in the library."""
    response = supabase.table("workouts").select("*").order("created_at", desc=True).execute()
    # Safely handle the response data
    return response.data if hasattr(response, 'data') else []

def get_workout_today():
    """Gets the currently active workout linked in workout_today."""
    try:
        response = supabase.table("workout_today").select("video_id, workouts(*)").eq("id", 1).single().execute()
        return response.data
    except Exception:
        return None

def update_workout_today(video_id):
    """Swaps the 'Today' workout to a new video_id."""
    return supabase.table("workout_today").update({"video_id": video_id, "updated_at": "now()"}).eq("id", 1).execute()

def delete_workout(video_id):
    """Deletes a workout (The SQL CASCADE handles the rest)."""
    return supabase.table("workouts").delete().eq("video_id", video_id).execute()

def log_completed_workout(video_id):
    """Logs a completion record in the progress table."""
    return supabase.table("progress").insert({"video_id": video_id}).execute()

def get_weekly_progress():
    """Counts how many workouts were completed in the last 7 days."""
    last_week = (datetime.now() - timedelta(days=7)).isoformat()
    response = supabase.table("progress").select("id").gte("completed_at", last_week).execute()
    return len(response.data) if response.data else 0

# --- NEW UPDATES ADDED BELOW ---

def discover_new_workout():
    """Picks a random workout from the library and updates 'Today'."""
    workouts = get_all_workouts()
    if not workouts:
        return None
    
    # Pick a random one from the list
    random_workout = random.choice(workouts)
    new_id = random_workout['video_id']
    
    # Update the 'workout_today' table in Supabase
    update_workout_today(new_id)
    return random_workout['url']

def add_workout_by_url(url):
    """
    Helper for the sidebar to add a workout using just a link.
    This connects the database to your yt_extractor logic.
    """
    import yt_extractor
    metadata = yt_extractor.get_video_metadata(url)
    if metadata:
        add_workout(
            video_id=metadata['video_id'],
            title=metadata['title'],
            url=metadata['url'],
            channel=metadata['channel'],
            duration=metadata['duration_seconds']
        )
        return True
    return False