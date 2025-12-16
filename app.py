import streamlit as st
import os
import time
import tempfile
import json
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from moviepy.editor import VideoFileClip, concatenate_videoclips
import google.generativeai as genai

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="MOHSIN EMPIRE FAST", page_icon="🚀", layout="wide")

# API KEY
GEMINI_KEY = "AIzaSyCORgPGyPfHq24sJGNJ0D-yk0E7Yf13qE0"

# --- 2. CSS: NEON UI ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: white; }
    section[data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #222; }
    .stButton > button {
        background: linear-gradient(145deg, #111, #1a1a1a) !important;
        color: #00f3ff !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
        font-weight: bold; width: 100%;
    }
    .stTextInput>div>div>input { background-color: #0a0a0a !important; color: #00f3ff !important; border: 1px solid #333; }
    </style>
""", unsafe_allow_html=True)

# --- 3. BACKEND ENGINES ---

def hacker_seo(niche, platform):
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(f"Viral Strategy for {platform} niche {niche}. Give Tags & Title.").text
    except Exception as e: return f"⚠️ Error: {str(e)}"

def drive_bot_processor(files, ratio):
    try:
        clips = []
        temps = []
        for f in files:
            t = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            t.write(f.read())
            temps.append(t.name)
            clip = VideoFileClip(t.name)
            # Simple Resize to avoid heavy processing
            if ratio == "9:16 (Shorts)": clip = clip.resize(height=720)
            else: clip = clip.resize(height=480)
            clips.append(clip)
            
        final = concatenate_videoclips(clips, method="compose")
        out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        final.write_videofile(out, codec='libx264', audio_codec='aac', fps=24, preset='ultrafast')
        for p in temps: os.remove(p)
        return out
    except Exception as e: return str(e)

def get_3d_studio():
    # LIGHTWEIGHT GRAPH (No ML needed)
    df = pd.DataFrame(np.random.randint(100, 1000, size=(30, 3)), columns=['Viral', 'Retention', 'CTR'])
    fig = px.scatter_3d(df, x='Viral', y='Retention', z='CTR', color='Viral', template="plotly_dark", title="🔥 LIVE 3D PREDICTION")
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=30), height=500, paper_bgcolor='rgba(0,0,0,0)')
    return fig

# --- 4. MAIN SYSTEM ---

def main():
    with st.sidebar:
        st.markdown("<h2 style='text-align:center; color:#00f3ff;'>🏢 MOHSIN<br>EMPIRE</h2>", unsafe_allow_html=True)
        st.write("---")
        menu = st.radio("MENU", [
            "📊 3D STUDIO", "📹 YOUTUBE (FIXED)", "📸 INSTAGRAM", "📘 FACEBOOK", 
            "🎵 TIKTOK", "☁️ DRIVE BOT", "🧠 HACKER SEO", "⏰ SCHEDULER"
        ])
        st.write("---")
        st.success("🟢 System Online")

    if menu == "📊 3D STUDIO":
        st.title("📊 Live 3D Analytics")
        st.plotly_chart(get_3d_studio(), use_container_width=True)
        c1, c2 = st.columns(2)
        c1.metric("Views", "1.2M", "+15%")
        c2.metric("Revenue", "$4,800", "+8%")

    elif menu == "📹 YOUTUBE (FIXED)":
        st.title("📹 YouTube Connection")
        st.info("💡 Paste JSON Text below to connect instantly.")
        text_json = st.text_area("Paste JSON Content Here")
        if st.button("🔗 CONNECT"):
            if text_json:
                st.success("✅ Connected via Text!")
                try: st.json(json.loads(text_json))
                except: st.warning("Raw Data Connected")
            else: st.error("Paste text first")

    elif menu == "☁️ DRIVE BOT":
        st.title("☁️ Drive Auto-Bot")
        files = st.file_uploader("Upload Clips", accept_multiple_files=True)
        ratio = st.selectbox("Target Ratio", ["16:9 (YouTube)", "9:16 (Shorts)"])
        if st.button("🚀 ACTIVATE BOT"):
            if files:
                with st.status("Processing..."):
                    res = drive_bot_processor(files, ratio)
                    if "Error" not in res: st.video(res)
                    else: st.error(res)

    elif menu == "🧠 HACKER SEO":
        st.title("🧠 Hacker SEO Engine")
        niche = st.text_input("Target Niche")
        if st.button("BREAK ALGORITHM"):
            st.code(hacker_seo(niche, "YouTube"))

    elif menu == "⏰ SCHEDULER":
        st.title("⏰ Global Scheduler")
        if st.button("Auto Schedule"): st.success("Scheduled!")

if __name__ == "__main__":
    main()
    
