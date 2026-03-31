import streamlit as st
import streamlit.components.v1 as components
import database_service as db
import email_service
import style

st.set_page_config(page_title="CyberProto Fitness", page_icon="💪", layout="wide")
try:
    style.apply_custom_css()
except:
    pass

st.markdown('<p class="main-title">🏋️‍♂️ CyberProto Fitness Discovery</p>', unsafe_allow_html=True)

# Always fetch fresh data
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


# Sidebar — Add Custom URL
st.sidebar.header("Add Custom URL")
yt_url = st.sidebar.text_input("YouTube Link:")
if st.sidebar.button("Add to Library"):
    if yt_url:
        with st.spinner("Fetching video info..."):
            success = db.add_workout_by_url(yt_url)
        if success:
            st.sidebar.success("Video added and now playing!")
            st.rerun()
        else:
            st.sidebar.error("Could not fetch video. Check the URL and try again.")
    else:
        st.sidebar.warning("Please enter a YouTube URL first.")

# Main UI
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔥 Active Workout")

    # Safely extract workout from Supabase joined response
    workout = None
    if today_data and isinstance(today_data, dict):
        raw = today_data.get('workouts')
        if isinstance(raw, list) and len(raw) > 0:
            workout = raw[0]
        elif isinstance(raw, dict):
            workout = raw

    if workout:
        embed_youtube(workout.get('url'))
        st.info(f"Currently Playing: **{workout.get('title', 'Unknown')}**")
        if workout.get('channel'):
            st.caption(f"Channel: {workout.get('channel')}")

        if st.button("✅ Mark as Completed"):
            db.log_completed_workout(workout.get('video_id'))
            st.balloons()
            st.success("Workout logged! Great job. 🎉")
    else:
        st.info("👈 Click **Discover New Workout** to get started!")

with col2:
    st.subheader("Discovery Controls")

    if st.button("🎲 Discover New Workout", use_container_width=True):
        with st.spinner("Searching YouTube for a workout..."):
            metadata = db.discover_new_workout()
        if metadata:
            email_service.send_workout_email(metadata['title'], metadata['url'])
            st.success(f"Found: **{metadata['title']}**")
            st.rerun()
        else:
            st.error("Could not find a workout. Check your YouTube API Key.")

    st.markdown("---")
    st.subheader("📈 Weekly Consistency")
    total_done = db.get_weekly_progress()
    st.metric("Workouts Completed", f"{total_done} this week")
    progress_val = min(total_done / 5, 1.0)
    st.progress(progress_val)

    st.markdown("---")
    st.subheader("Your Library")
    if all_workouts:
        for w in all_workouts[:5]:
            c = st.columns([4, 1])
            c[0].write(f"• {w.get('title', 'Workout')[:25]}...")
            if c[1].button("🗑️", key=w.get('video_id')):
                db.delete_workout(w.get('video_id'))
                st.rerun()
    else:
        st.write("No saved workouts yet.")