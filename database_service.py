import os
import random
import requests
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

SUPABASE_URL = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")
YOUTUBE_API_KEY = st.secrets.get("YOUTUBE_API_KEY") or os.getenv("YOUTUBE_API_KEY")

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


def search_youtube_workout():
    """Searches YouTube for a random workout video and returns its metadata."""
    search_terms = [
        "full body workout", "HIIT workout", "morning workout routine",
        "strength training", "cardio workout", "abs workout",
        "leg day workout", "home workout no equipment", "yoga workout",
        "boxing workout"
    ]
    query = random.choice(search_terms)

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "videoCategoryId": "17",  # Sports category
        "maxResults": 10,
        "key": YOUTUBE_API_KEY
    }

    try:
        response = requests.get("https://www.googleapis.com/youtube/v3/search", params=params)
        results = response.json().get("items", [])
        if not results:
            return None

        # Pick a random result from the top 10
        picked = random.choice(results)
        video_id = picked["id"]["videoId"]
        title = picked["snippet"]["title"]
        channel = picked["snippet"]["channelTitle"]
        url = f"https://www.youtube.com/watch?v={video_id}"

        return {
            "video_id": video_id,
            "title": title,
            "channel": channel,
            "url": url,
            "duration_seconds": None
        }
    except Exception as e:
        print(f"YouTube search error: {e}")
        return None


def discover_new_workout():
    """Searches YouTube for a new workout, saves it, and sets it as today's workout."""
    current_id = get_current_video_id()

    # Keep searching until we get a different video
    for _ in range(5):
        metadata = search_youtube_workout()
        if metadata and metadata["video_id"] != current_id:
            # Save to library and set as today
            add_workout(
                video_id=metadata["video_id"],
                title=metadata["title"],
                url=metadata["url"],
                channel=metadata["channel"],
                duration=metadata["duration_seconds"]
            )
            update_workout_today(metadata["video_id"])
            return metadata
    return None


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
            update_workout_today(metadata['video_id'])
            return True
    except Exception as e:
        print(f"Extraction error: {e}")
    return False