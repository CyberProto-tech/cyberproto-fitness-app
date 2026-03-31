import streamlit as st
import database_service as db
import email_service
import style

st.set_page_config(page_title="CyberProto Fitness", page_icon="💪", layout="wide")
try:
    style.apply_custom_css()
except:
    pass

st.markdown('<p class="main-title">🏋️‍♂️ CyberProto Fitness Discovery</p>', unsafe_allow_html=True)

# Always fetch fresh data at the top of every run
all_workouts = db.get_all_workouts()
today_data = db.get_workout_today()

# Sidebar
st.sidebar.header("Add Custom URL")
yt_url = st.sidebar.text_input("YouTube Link:")
if st.sidebar.button("Add to Library"):
    if yt_url:
        with st.spinner("Fetching video info..."):
            success = db.add_workout_by_url(yt_url)
        if success:
            st.sidebar.success("Video added and set as today's workout!")
            st.rerun()
        else:
            st.sidebar.error("Could not fetch video. Check the URL and try again.")

# Main UI
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔥 Active Workout")

    # Safely extract the workout dict from the joined Supabase response
    workout = None
    if today_data and isinstance(today_data, dict):
        raw = today_data.get('workouts')
        # Supabase join can return a dict or a list — handle both
        if isinstance(raw, list) and len(raw) > 0:
            workout = raw[0]
        elif isinstance(raw, dict):
            workout = raw

    if workout:
        video_url = workout.get('url')
        if video_url:
            st.video(video_url)
        st.info(f"Currently Playing: **{workout.get('title', 'Unknown')}**")

        if st.button("✅ Mark as Completed"):
            db.log_completed_workout(workout.get('video_id'))
            st.balloons()
            st.success("Workout logged! Great job.")
    else:
        st.info("Click 'Discover' to find a workout, or add a URL in the sidebar!")

with col2:
    st.subheader("Discovery Controls")
    if st.button("🎲 Discover New Workout", use_container_width=True):
        with st.spinner("Scouring your library for a new workout..."):
            new_url = db.discover_new_workout()
            if new_url:
                # Fetch updated data to get title for email
                fresh_today = db.get_workout_today()
                fresh_workout = None
                if fresh_today and isinstance(fresh_today, dict):
                    raw = fresh_today.get('workouts')
                    if isinstance(raw, list) and len(raw) > 0:
                        fresh_workout = raw[0]
                    elif isinstance(raw, dict):
                        fresh_workout = raw

                if fresh_workout:
                    email_service.send_workout_email(
                        fresh_workout.get('title'),
                        fresh_workout.get('url')
                    )
                st.rerun()
            else:
                st.warning("No workouts in your library yet! Add one via the sidebar.")

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
        st.write("Your library is empty. Add a workout above!")