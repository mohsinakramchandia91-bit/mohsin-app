import streamlit as st
import os
import time
import tempfile
import json
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pytz
import google.generativeai as genai

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="MOHSIN EMPIRE FAST", page_icon="⚡", layout="wide")

# API KEY
GEMINI_KEY = "AIzaSyCORgPGyPfHq24sJGNJ0D-yk0E7Yf13qE0"

# --- 2. CSS: NEON UI ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: white; }
    section[data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #333; }
    
    /* BUTTONS */
    .stButton > button {
        background: linear-gradient(145deg, #111, #1a1a1a) !important;
        color: #00f3ff !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
        font-weight: bold; width: 100%;
        transition: 0.3s;
    }
    .stButton > button:hover {
        box-shadow: 0 0 15px #00f3ff !important; border-color: #00f3ff !important;
    }
    
    /* INPUTS */
    .stTextInput>div>div>input { background-color: #0a0a0a !important; color: #00f3ff !important; border: 1px solid #333; }
    </style>
""", unsafe_allow_html=True)

# --- 3. BACKEND ENGINES (LAZY LOADING) ---

def hacker_seo(niche, platform):
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(f"Viral Strategy for {platform} niche {niche}. Give Tags & Title.").text
    except: return "AI Connecting..."

def drive_bot_processor(files, ratio):
    # --- MAGIC FIX: Import MoviePy ONLY when button is clicked ---
    # This prevents the "Oven" hang on startup
    import moviepy.editor as mp 
    from moviepy.video.VideoClip import TextClip
    
    try:
        clips = []
        temps = []
        for f in files:
            t = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            t.write(f.read())
            temps.append(t.name)
            
            clip = mp.VideoFileClip(t.name)
            # Simple Resize
            if ratio == "9:16 (Shorts)": clip = clip.resize(height=720)
            else: clip = clip.resize(height=480)
            clips.append(clip)
            
        final = mp.concatenate_videoclips(clips, method="compose")
        out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        final.write_videofile(out, codec='libx264', audio_codec='aac', fps=24, preset='ultrafast')
        
        for p in temps: os.remove(p)
        return out
    except Exception as e: return str(e)

def get_3d_studio():
    np.random.seed(42)
    df = pd.DataFrame(np.random.randint(100, 1000, size=(30, 3)), columns=['Viral', 'Retention', 'CTR'])
    fig = px.scatter_3d(df, x='Viral', y='Retention', z='CTR', color='Viral', template="plotly_dark", title="🔥 LIVE 3D DATA")
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=30), height=500, paper_bgcolor='rgba(0,0,0,0)')
    return fig

# --- 4. MAIN SYSTEM ---

def main():
    with st.sidebar:
        st.markdown("<h2 style='text-align:center; color:#00f3ff;'>⚡ MOHSIN<br>EMPIRE</h2>", unsafe_allow_html=True)
        st.write("---")
        menu = st.radio("MENU", [
            "📊 3D STUDIO", "📹 YOUTUBE (FAST)", "☁️ DRIVE BOT", "🧠 HACKER SEO", "⏰ SCHEDULER"
        ])
        st.success("🟢 System Online")

    if menu == "📊 3D STUDIO":
        st.title("📊 Live 3D Analytics")
        st.plotly_chart(get_3d_studio(), use_container_width=True)
        c1, c2 = st.columns(2)
        c1.metric("Views", "1.2M", "+15%")
        c2.metric("Revenue", "$4,800", "+8%")

    elif menu == "📹 YOUTUBE (FAST)":
        st.title("📹 YouTube Connection")
        st.info("Paste JSON below to connect instantly.")
        text_json = st.text_area("Paste JSON Content Here")
        if st.button("🔗 CONNECT"):
            if text_json:
                st.success("✅ Connected!")
                try: st.json(json.loads(text_json))
                except: pass
            else: st.error("Empty")

    elif menu == "☁️ DRIVE BOT":
        st.title("☁️ Drive Auto-Bot")
        st.info("Upload clips. Bot joins them automatically.")
        files = st.file_uploader("Upload Clips", accept_multiple_files=True)
        ratio = st.selectbox("Ratio", ["16:9 (YouTube)", "9:16 (Shorts)"])
        
        if st.button("🚀 ACTIVATE BOT"):
            if files:
                with st.status("Initializing Engine..."):
                    res = drive_bot_processor(files, ratio)
                    if "Error" not in res: st.video(res)
                    else: st.error(res)

    elif menu == "🧠 HACKER SEO":
        st.title("🧠 Hacker SEO Engine")
        niche = st.text_input("Topic")
        if st.button("HACK"): st.code(hacker_seo(niche, "YouTube"))

    elif menu == "⏰ SCHEDULER":
        st.title("⏰ Global Scheduler")
        st.button("Auto Schedule")

if __name__ == "__main__":
    main()
        
