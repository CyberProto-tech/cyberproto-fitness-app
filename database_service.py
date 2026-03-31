import os
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
    return response.data

def get_workout_today():
    """Gets the currently active workout linked in workout_today."""
    response = supabase.table("workout_today").select("video_id, workouts(*)").eq("id", 1).single().execute()
    return response.data

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