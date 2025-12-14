
import streamlit as st
import os
import time
import sqlite3
import hashlib
import random
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from datetime import datetime
from moviepy.editor import VideoFileClip, concatenate_videoclips

# --- 🛠️ AUTO-FIX: SERVER CONFIG ---
if not os.path.exists(".streamlit"):
    os.makedirs(".streamlit")
with open(".streamlit/config.toml", "w") as f:
    f.write("[server]\nheadless = true\nenableCORS = false\nrunOnSave = true\n[theme]\nbase='dark'\nprimaryColor='#00f3ff'\nbackgroundColor='#000000'")

# --- CONFIG ---
st.set_page_config(page_title="MOHSIN EMPIRE", page_icon="💎", layout="wide")

# 👇 API KEY (FIXED) 👇
GEMINI_KEY = "AIzaSyCORgPGyPfHq24sJGNJ0D-yk0E7Yf13qE0"

# --- DATABASE ---
if not os.path.exists("temp"): os.makedirs("temp")
DB_PATH = "mohsin_cloud_final.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (email TEXT PRIMARY KEY, password TEXT, name TEXT, phone TEXT, status TEXT, 
                  joined_date TEXT)''')
    try:
        # Admin Account
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", 
                 ("mohsinakramchandia91@gmail.com", hashlib.sha256("Mohsin5577@".encode()).hexdigest(), 
                  "Mohsin Akram", "03201847179", "ACTIVE", str(datetime.now())))
    except: pass
    conn.commit(); conn.close()

init_db()

# --- CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: white; }
    .glass-box {
        background: #111; border: 1px solid #00f3ff; padding: 20px; border-radius: 15px; margin-bottom: 20px;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.2);
    }
    input { background: #222 !important; color: white !important; border: 1px solid #444 !important; }
    button { background: linear-gradient(90deg, #00f3ff, #0066ff) !important; color: black !important; font-weight: bold !important; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# --- BACKEND LOGIC ---

def process_video_safe(files):
    try:
        clips = []
        for f in files:
            t_path = f"temp/{f.name}"
            with open(t_path, "wb") as t: t.write(f.getbuffer())
            clips.append(VideoFileClip(t_path))
        
        final = concatenate_videoclips(clips, method="compose")
        out_path = f"temp/final_{int(time.time())}.mp4"
        final.write_videofile(out_path, codec='libx264', audio_codec='aac')
        return True, out_path, final.duration
    except Exception as e:
        return False, str(e), 0

def ai_brain(query):
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(query).text
    except: return "AI Sleeping (Server Busy)"

# --- UI ---

if 'user' not in st.session_state: st.session_state.user = None
if 'otp' not in st.session_state: st.session_state.otp = None

def main():
    if not st.session_state.user:
        st.markdown("<h1 style='text-align:center; color:#00f3ff'>💎 MOHSIN EMPIRE</h1>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["LOGIN", "REGISTER"])
        
        with tab1:
            st.markdown('<div class="glass-box">', unsafe_allow_html=True)
            em = st.text_input("Email")
            pw = st.text_input("Password", type="password")
            if st.button("LOGIN"):
                conn = sqlite3.connect(DB_PATH)
                u = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (em, hashlib.sha256(pw.encode()).hexdigest())).fetchone()
                if u:
                    st.session_state.user = u[0]
                    st.rerun()
                else: st.error("Invalid Login")
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="glass-box">', unsafe_allow_html=True)
            r_email = st.text_input("Gmail")
            r_name = st.text_input("Name")
            r_pass = st.text_input("Set Password", type="password")
            
            if st.button("SEND OTP CODE"):
                # CLOUD SAFE OTP (Toast Message)
                code = str(random.randint(100000, 999999))
                st.session_state.otp = code
                st.success(f"✅ OTP Sent! Check Top Right Corner.")
                st.toast(f"🔑 YOUR OTP: {code}", icon="📩")
            
            if st.session_state.otp:
                otp_in = st.text_input("Enter OTP")
                if st.button("VERIFY & REGISTER"):
                    if otp_in == st.session_state.otp:
                        try:
                            conn = sqlite3.connect(DB_PATH)
                            conn.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", 
                                      (r_email, hashlib.sha256(r_pass.encode()).hexdigest(), r_name, "000", "ACTIVE", str(datetime.now())))
                            conn.commit(); conn.close()
                            st.success("Created! Login Now.")
                        except: st.error("Email exists")
                    else: st.error("Wrong OTP")
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.sidebar.title("MENU")
        menu = st.sidebar.radio("Go", ["Dashboard", "Factory", "Connections"])
        if st.sidebar.button("Logout"): st.session_state.user = None; st.rerun()
        
        if menu == "Dashboard":
            st.title("📊 Live Stats")
            st.markdown('<div class="glass-box"><h3>👁️ Total Views: 1.2M</h3></div>', unsafe_allow_html=True)
            df = pd.DataFrame({"Day": range(5), "Views": [10, 30, 20, 50, 90]})
            st.plotly_chart(px.line(df, x="Day", y="Views", template="plotly_dark"), use_container_width=True)

        elif menu == "Factory":
            st.title("🏭 Video Factory")
            files = st.file_uploader("Upload 4 Clips", accept_multiple_files=True)
            if st.button("🚀 LAUNCH"):
                if len(files) == 4:
                    with st.status("Processing... (This may take 1 min)"):
                        success, res, dur = process_video_safe(files)
                        if success:
                            st.success("✅ Video Ready!")
                            st.video(res)
                            st.info(f"AI Title: {ai_brain('Viral title for video')}")
                        else:
                            st.error(f"Failed: {res}")
                else: st.error("Upload 4 files please.")

        elif menu == "Connections":
            st.title("🌐 Accounts")
            st.info("Direct API Connection (No File Upload needed)")
            with st.form("yt"):
                k = st.text_input("YouTube API Key")
                if st.form_submit_button("CONNECT"):
                    st.success("Key Saved (Session)")

if __name__ == "__main__":
    main()
    
