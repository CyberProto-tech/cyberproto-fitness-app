import streamlit as st
import database_service as db
import email_service
import style

st.set_page_config(page_title="CyberProto Fitness", page_icon="💪", layout="wide")
try: style.apply_custom_css()
except: pass

st.markdown('<p class="main-title">🏋️‍♂️ CyberProto Fitness Discovery</p>', unsafe_allow_html=True)

# Data Refresh
all_workouts = db.get_all_workouts()
today_data = db.get_workout_today()

# Sidebar
st.sidebar.header("Add Custom URL")
yt_url = st.sidebar.text_input("YouTube Link:")
if st.sidebar.button("Add to Library"):
    # Note: Using your existing function add_workout_by_url
    if yt_url and db.add_workout_by_url(yt_url):
        st.rerun()

# Main UI
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔥 Active Workout")
    
    # FIX: We check if today_data is a dictionary and has 'workouts'
    if today_data and isinstance(today_data, dict) and 'workouts' in today_data:
        workout = today_data['workouts']
        st.video(workout.get('url'))
        st.info(f"Currently Playing: **{workout.get('title')}**")
        
        if st.button("✅ Mark as Completed"):
            db.log_completed_workout(workout.get('video_id'))
            st.balloons()
            st.success("Workout logged! Great job.")
    else:
        st.info("Click 'Discover' to find a workout!")

with col2:
    st.subheader("Discovery Controls")
    if st.button("🎲 Discover New Workout", use_container_width=True):
        with st.spinner("Scouring YouTube for pro trainers..."):
            new_url = db.discover_new_workout()
            if new_url:
                # Re-fetch data to get the new selection
                fresh_today = db.get_workout_today()
                if fresh_today and 'workouts' in fresh_today:
                    workout_info = fresh_today['workouts']
                    email_service.send_workout_email(workout_info.get('title'), workout_info.get('url'))
                    st.rerun()

    st.markdown("---")
    st.subheader("📈 Weekly Consistency")
    total_done = db.get_weekly_progress()
    st.metric("Workouts Completed", f"{total_done} this week")
    progress_val = min(total_done / 5, 1.0)
    st.progress(progress_val)

    st.markdown("---")
    st.subheader("Your Library")
    if all_workouts:
        for w in all_workouts[:5]: # Show last 5
            c = st.columns([4, 1])
            c[0].write(f"• {w.get('title', 'Workout')[:25]}...")
            if c[1].button("🗑️", key=w.get('video_id')):
                db.delete_workout(w.get('video_id'))
                st.rerun()