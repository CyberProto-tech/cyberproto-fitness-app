import os
import random
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

SUPABASE_URL = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Missing Supabase Credentials! Please check your .env file or Streamlit Secrets.")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def add_workout(video_id, title, url, channel=None, duration=None):
    data = {
        "video_id": video_id,
        "title": title,
        "url": url,
        "channel": channel,
        "duration_seconds": duration
    }
    return supabase.table("workouts").upsert(data).execute()


def get_all_workouts():
    response = supabase.table("workouts").select("*").order("created_at", desc=True).execute()
    return response.data if hasattr(response, 'data') else []


def get_workout_today():
    """Gets the currently active workout linked in workout_today."""
    try:
        response = supabase.table("workout_today").select("video_id, workouts(*)").eq("id", 1).single().execute()
        return response.data
    except Exception:
        return None


def get_current_video_id():
    """Returns just the current video_id from workout_today."""
    try:
        response = supabase.table("workout_today").select("video_id").eq("id", 1).single().execute()
        if response.data:
            return response.data.get("video_id")
    except Exception:
        pass
    return None


def update_workout_today(video_id):
    now_ts = datetime.now().isoformat()
    return supabase.table("workout_today").update({
        "video_id": video_id,
        "updated_at": now_ts
    }).eq("id", 1).execute()


def delete_workout(video_id):
    return supabase.table("workouts").delete().eq("video_id", video_id).execute()


def log_completed_workout(video_id):
    return supabase.table("progress").insert({"video_id": video_id}).execute()


def get_weekly_progress():
    last_week = (datetime.now() - timedelta(days=7)).isoformat()
    response = supabase.table("progress").select("id").gte("completed_at", last_week).execute()
    return len(response.data) if response.data else 0


def discover_new_workout():
    """Picks a DIFFERENT random workout from the library and updates Today."""
    workouts = get_all_workouts()
    if not workouts:
        return None

    current_id = get_current_video_id()

    # Filter out the currently playing video so we always get something new
    other_workouts = [w for w in workouts if w['video_id'] != current_id]

    # If only one video exists, just use it
    if not other_workouts:
        other_workouts = workouts

    random_workout = random.choice(other_workouts)
    update_workout_today(random_workout['video_id'])
    return random_workout['url']


def add_workout_by_url(url):
    """Adds a workout from a YouTube URL and sets it as today's workout."""
    try:
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
            # Immediately set the new video as today's workout
            update_workout_today(metadata['video_id'])
            return True
    except Exception as e:
        print(f"Extraction error: {e}")
    return False