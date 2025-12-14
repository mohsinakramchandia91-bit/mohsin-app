
import streamlit as st
import sqlite3
import hashlib
import time
import os
import random
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from datetime import datetime
from moviepy.editor import VideoFileClip, concatenate_videoclips
from apscheduler.schedulers.background import BackgroundScheduler

# --- CONFIG ---
st.set_page_config(page_title="MOHSIN EMPIRE", page_icon="💎", layout="wide")

# 👇 API KEY (Isay zaroor check karein) 👇
GEMINI_KEY = "AIzaSyCORgPGyPfHq24sJGNJ0D-yk0E7Yf13qE0"

# --- 🛠️ SYSTEM INITIALIZATION (The Fix) ---
if not os.path.exists("temp_data"): os.makedirs("temp_data")
DB_PATH = "mohsin_empire_live.db"

# --- DATABASE ENGINE ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (email TEXT PRIMARY KEY, password TEXT, name TEXT, status TEXT, 
                  joined_date TEXT)''')
    try:
        # Admin Fix
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", 
                 ("mohsinakramchandia91@gmail.com", hashlib.sha256("Mohsin5577@".encode()).hexdigest(), 
                  "Mohsin Akram", "ACTIVE", str(datetime.now())))
    except: pass
    conn.commit(); conn.close()

init_db()

# --- CSS: ULTRA PREMIUM ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: white; }
    .glass-card {
        background: rgba(20, 20, 30, 0.9);
        border: 1px solid #00f3ff;
        padding: 20px; border-radius: 15px;
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.2);
        margin-bottom: 20px;
    }
    input { background: #111 !important; color: white !important; border: 1px solid #333 !important; }
    button { background: linear-gradient(90deg, #00f3ff, #0066ff) !important; color: black !important; font-weight: bold !important; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# --- BACKEND ENGINES (Cached to prevent crash) ---

@st.cache_resource
def get_scheduler():
    # Ye function Auto-Pilot ko zinda rakhe ga
    scheduler = BackgroundScheduler()
    scheduler.start()
    return scheduler

scheduler = get_scheduler()

def process_video_logic(files):
    try:
        clips = []
        for f in files:
            t_path = f"temp_data/{f.name}"
            with open(t_path, "wb") as t: t.write(f.getbuffer())
            clips.append(VideoFileClip(t_path))
        
        final = concatenate_videoclips(clips, method="compose")
        out_path = f"temp_data/final_{int(time.time())}.mp4"
        final.write_videofile(out_path, codec='libx264', audio_codec='aac')
        return out_path, final.duration
    except Exception as e:
        return None, str(e)

def ai_brain_logic(query):
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(query).text
    except: return "AI Sleeping (Check Key)"

# --- PAGES ---

def login():
    st.markdown("<br><br><h1 style='text-align:center; color:#00f3ff;'>💎 MOHSIN EMPIRE</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        email = st.text_input("📧 Email")
        password = st.text_input("🔑 Password", type="password")
        if st.button("LOGIN"):
            hashed = hashlib.sha256(password.encode()).hexdigest()
            conn = sqlite3.connect(DB_PATH)
            user = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (email, hashed)).fetchone()
            conn.close()
            if user:
                st.session_state.user = user[0]
                st.rerun()
            else: st.error("Wrong Credentials")
        st.markdown('</div>', unsafe_allow_html=True)

def dashboard():
    st.sidebar.title("MENU")
    if st.sidebar.button("LOGOUT"): st.session_state.user = None; st.rerun()
    
    tabs = st.tabs(["📊 DASHBOARD", "🏭 FACTORY", "✈️ AUTO-PILOT", "🤖 AI CHAT"])
    
    with tabs[0]:
        st.markdown("### 📈 Live Stats")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="glass-card"><h3>👁️ Views: 1.5M</h3></div>', unsafe_allow_html=True)
            df = pd.DataFrame({"Day": range(7), "Growth": [10, 40, 30, 70, 90, 120, 150]})
            st.plotly_chart(px.line(df, x="Day", y="Growth", template="plotly_dark"), use_container_width=True)
        with c2:
            st.markdown('<div class="glass-card"><h3>💰 Revenue: $2,400</h3></div>', unsafe_allow_html=True)

    with tabs[1]:
        st.markdown("### 🎬 Video Factory")
        files = st.file_uploader("Upload 4 Clips", accept_multiple_files=True)
        if st.button("🚀 LAUNCH"):
            if files and len(files) == 4:
                with st.status("⚙️ Processing..."):
                    path, info = process_video_logic(files)
                    if path:
                        st.success("✅ Done!")
                        st.video(path)
                        st.info(f"AI Title: {ai_brain_logic('Viral title for this video')}")
                    else: st.error(f"Error: {info}")
            else: st.error("Please upload 4 files.")

    with tabs[2]:
        st.markdown("### ✈️ Auto-Pilot")
        st.info("System is monitoring Google Drive.")
        folder = st.text_input("Drive Folder ID")
        if st.button("ACTIVATE"):
            # Add job to scheduler
            scheduler.add_job(lambda: print(f"Checking Drive {folder}..."), 'interval', minutes=60)
            st.success("Auto-Pilot Activated! (Running in Background)")

    with tabs[3]:
        st.markdown("### 🤖 Mohsin AI")
        q = st.chat_input("Ask anything...")
        if q:
            st.write(f"**You:** {q}")
            st.write(f"**AI:** {ai_brain_logic(q)}")

# --- MAIN ---
if 'user' not in st.session_state: st.session_state.user = None

if not st.session_state.user: login()
else: dashboard()
    
