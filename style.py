import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* Main background and text */
        .stApp {
            background-color: #0E1117;
        }
        
        /* Custom Styling for the Title */
        .main-title {
            font-size: 45px;
            font-weight: 800;
            color: #00D4FF; /* Cyber Blue */
            text-shadow: 2px 2px 10px rgba(0, 212, 255, 0.3);
            margin-bottom: 0px;
        }
        
        /* Styling the Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #161B22;
            border-right: 1px solid #30363D;
        }

        /* Making Buttons look 'Techy' */
        .stButton>button {
            border-radius: 8px;
            border: 1px solid #00D4FF;
            background-color: transparent;
            color: #00D4FF;
            transition: 0.3s;
        }
        
        .stButton>button:hover {
            background-color: #00D4FF;
            color: white;
            box-shadow: 0px 0px 15px rgba(0, 212, 255, 0.5);
        }

        /* Workout Card Look */
        .workout-card {
            background-color: #1C2128;
            padding: 20px;
            border-radius: 15px;
            border: 1px solid #30363D;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)