import streamlit as st
import streamlit.components.v1 as components
import database_service as db
import email_service
import style

# Basic Page Setup
st.set_page_config(page_title="CyberProto Fitness", page_icon="💪", layout="wide")

# Apply custom styles
try:
    style.apply_custom_css()
except:
    pass

st.markdown('<p class="main-title">🏋️‍♂️ CyberProto Fitness Discovery</p>', unsafe_allow_html=True)

# 1. FETCH DATA: Always fetch fresh data from the database
all_workouts = db.get_all_workouts()
today_data = db.get_workout_today()

def extract_yt_id(url):
    """Extracts YouTube video ID from a URL."""
    if not url:
        return None
    if "watch?v=" in url:
        return url.split("watch?v=")[-1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    return None

def embed_youtube(url):
    """Renders a YouTube video as an embedded iframe."""
    yt_id = extract_yt_id(url)
    if yt_id:
        html = f"""
            <iframe width="100%" height="420"
                src="https://www.youtube.com/embed/{yt_id}?autoplay=0"
                frameborder="0"
                allow="accelerometer; autoplay; clipboard-write;
                       encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen>
            </iframe>
        """
        components.html(html, height=440)
    else:
        st.warning("Could not parse YouTube URL.")

# --- SIDEBAR: ADD CUSTOM URL ---
st.sidebar.header("Add Custom URL")
yt_url = st.sidebar.text_input("YouTube Link:")
if st.sidebar.button("Add to Library"):
    if yt_url:
        with st.spinner("Fetching video info..."):
            # This function in database_service handles metadata and saving
            success = db.add_workout_by_url(yt_url)
        if success:
            st.sidebar.success("Video added to library!")
            st.rerun()
        else:
            st.sidebar.error("Could not fetch video. Check the URL and try again.")
    else:
        st.sidebar.warning("Please enter a YouTube URL first.")

# --- MAIN UI LAYOUT ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔥 Active Workout")

    # LOGIC FIX: Extract workout from Supabase response
    workout = None
    
    # Check 1: Try to get the workout specifically set for today
    if today_data and isinstance(today_data, dict):
        raw = today_data.get('workouts')
        if isinstance(raw, list) and len(raw) > 0:
            workout = raw[0]
        elif isinstance(raw, dict):
            workout = raw
    
    # Check 2: Fallback - If today is empty, show the most recent video from the library
    if not workout and all_workouts:
        workout = all_workouts[0]

    # RENDERING: Show the video and info
    if workout:
        embed_youtube(workout.get('url'))
        st.info(f"Currently Playing: **{workout.get('title', 'Unknown Workout')}**")
        if workout.get('channel'):
            st.caption(f"Channel: {workout.get('channel')}")

        if st.button("✅ Mark as Completed"):
            db.log_completed_workout(workout.get('video_id'))
            st.balloons()
            st.success("Workout logged! Great job. 🎉")
            # Refresh to update the progress bar in col2
            st.rerun()
    else:
        # This only shows if BOTH today_data and all_workouts are empty
        st.info("👈 Your library is empty. Add a URL or click Discover to begin!")

with col2:
    st.subheader("Discovery Controls")

    if st.button("🎲 Discover New Workout", use_container_width=True):
        with st.spinner("Searching YouTube for a workout..."):
            # This searches YouTube, saves to DB, and updates today's ID
            metadata = db.discover_new_workout()
        if metadata:
            # Send the email update
            try:
                email_service.send_workout_email(metadata['title'], metadata['url'])
            except:
                pass
            st.success(f"Found: **{metadata['title']}**")
            st.rerun()
        else:
            st.error("Discovery failed. Check your YouTube API Key in Secrets.")

    st.markdown("---")
    st.subheader("📈 Weekly Consistency")
    total_done = db.get_weekly_progress()
    st.metric("Workouts Completed", f"{total_done} this week")
    
    # Goal of 5 workouts per week
    progress_val = min(total_done / 5, 1.0)
    st.progress(progress_val)

    st.markdown("---")
    st.subheader("Your Library")
    if all_workouts:
        # Show the 5 most recent videos in the library
        for w in all_workouts[:5]:
            c = st.columns([4, 1])
            title_crop = w.get('title', 'Workout')[:25]
            c[0].write(f"• {title_crop}...")
            # Unique key for each delete button using video_id
            if c[1].button("🗑️", key=f"del_{w.get('video_id')}"):
                db.delete_workout(w.get('video_id'))
                st.rerun()
    else:
        st.write("No saved workouts yet.")