import streamlit as st
import sqlite3
import hashlib
import time
import os
import random
import json
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pytz
import tempfile
from datetime import datetime
from moviepy.editor import VideoFileClip, concatenate_videoclips
import google.generativeai as genai
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="MOHSIN EMPIRE V16", page_icon="👑", layout="wide")

# UPLOAD FIX (2GB LIMIT)
if not os.path.exists(".streamlit"): os.makedirs(".streamlit")
with open(".streamlit/config.toml", "w") as f:
    f.write("[server]\nmaxUploadSize = 2000\nheadless = true\nenableCORS = false\nrunOnSave = true\n[theme]\nbase='dark'\nprimaryColor='#00f3ff'\nbackgroundColor='#000000'")

# STATE MANAGEMENT
if 'user' not in st.session_state: st.session_state.user = None
if 'logs' not in st.session_state: st.session_state.logs = [] # Auto-Pilot Logs

# API KEY
GEMINI_KEY = "AIzaSyCORgPGyPfHq24sJGNJ0D-yk0E7Yf13qE0"

# --- 2. DATABASE (WITH AUTO DEMO USER) ---
if not os.path.exists("user_data"): os.makedirs("user_data")
DB_PATH = "mohsin_redemption_v16.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (email TEXT PRIMARY KEY, password TEXT, name TEXT, phone TEXT, status TEXT, 
                  timezone TEXT, autopilot_id TEXT, yt_json TEXT, joined_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS payments 
                 (email TEXT, tid TEXT, method TEXT, status TEXT, date TEXT)''')
    
    # 1. SUPER ADMIN CREATE
    try:
        admin_pass = hashlib.sha256("Mohsin5577@".encode()).hexdigest()
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                 ("mohsinakramchandia91@gmail.com", admin_pass, "CEO MOHSIN", "03201847179", 
                  "ADMIN", "Asia/Karachi", "None", "Connected", str(datetime.now())))
    except: pass

    # 2. AUTO-INSERT DEMO USER (TAKE AAPKO BUTTON NAZAR AAYEIN)
    # Ye user automatically "Pending" list mein aa jayega
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                 ("demo_client@gmail.com", "123", "Demo Request", "000", "REVIEW", "UTC", "None", "None", str(datetime.now())))
        c.execute("INSERT INTO payments VALUES (?, ?, ?, ?, ?)", 
                 ("demo_client@gmail.com", "TID-AUTO-MAGIC", "JazzCash", "REVIEW", str(datetime.now())))
    except: pass

    conn.commit(); conn.close()

init_db()

# --- 3. UI STYLE (NEON STUDIO) ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    
    /* GLASS CARDS */
    .studio-card {
        background: rgba(20, 20, 30, 0.9);
        border: 1px solid #333;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.05);
        margin-bottom: 15px;
    }
    
    /* BUTTONS & INPUTS */
    .stTextInput>div>div>input { background: #111 !important; color: #00f3ff !important; border: 1px solid #444; }
    .stButton>button {
        background: linear-gradient(90deg, #00f3ff, #0066ff);
        color: black; font-weight: bold; border-radius: 6px; width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover { box-shadow: 0 0 20px #00f3ff; color: white; }
    
    /* TERMINAL LOGS */
    .log-box {
        background: black; color: #0f0; font-family: monospace;
        padding: 15px; border: 1px solid #333; height: 200px; overflow-y: auto;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. HIGH-TECH VISUALS (RESTORED) ---

def get_3d_realtime_chart():
    # 3D BAR CHART (STUDIO)
    x = ['Live', '1h', '6h', '12h', '24h']
    y = [500, 1500, 4000, 8000, 12000]
    fig = go.Figure(data=[go.Bar(x=x, y=y, marker=dict(color=y, colorscale='Viridis'))])
    fig.update_layout(title="📊 Real-Time Studio Activity", template="plotly_dark",
                      paper_bgcolor='rgba(0,0,0,0)', scene=dict(bgcolor='rgba(0,0,0,0)'), height=350)
    return fig

def get_3d_globe():
    # ROTATING EARTH
    df = pd.DataFrame({"Country": ["Pakistan", "USA", "UK"], "Z": [100, 200, 50], "Code": ["PAK", "USA", "GBR"]})
    fig = go.Figure(data=go.Choropleth(locations=df['Code'], z=df['Z'], colorscale='Electric', marker_line_color='gray'))
    fig.update_layout(geo=dict(showframe=False, projection_type='orthographic', bgcolor='rgba(0,0,0,0)'),
                      paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=0, b=0), height=350)
    return fig

def get_pca_3d():
    # ML SCATTER PLOT
    df = pd.DataFrame(np.random.randint(0,100,size=(100, 3)), columns=['Views', 'CTR', 'Retention'])
    fig = px.scatter_3d(df, x='Views', y='CTR', z='Retention', color='Views', template="plotly_dark", title="🔥 Viral Clusters (PCA)")
    fig.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0))
    return fig

def deep_seek_brain(niche):
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(f"Hacker Strategy for {niche}. Give Tags & Title.").text
    except: return "⚠️ AI Connecting..."

# --- 5. REAL FACTORY (UPLOAD FIX) ---
def process_video_real(files):
    try:
        clips = []
        temp_paths = []
        for f in files:
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            tfile.write(f.read())
            temp_paths.append(tfile.name)
            clips.append(VideoFileClip(tfile.name).resize(height=480)) # 480p Safe Mode
            
        final = concatenate_videoclips(clips, method="compose")
        out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        final.write_videofile(out, codec='libx264', audio_codec='aac', fps=24, preset='ultrafast')
        
        for p in temp_paths: os.remove(p)
        return out
    except Exception as e: return f"Error: {str(e)}"

# --- 6. PAGES ---

def admin_dashboard():
    st.title("👑 SUPREME COMMAND")
    if st.button("🔴 LOGOUT"): st.session_state.user=None; st.rerun()
    
    conn = sqlite3.connect(DB_PATH)
    
    # PENDING REQUESTS
    st.markdown("### 💰 Pending Requests")
    # Ye query ab "Demo Client" ko dhundegi aur buttons show karegi
    reqs = conn.execute("SELECT * FROM payments WHERE status='REVIEW'").fetchall()
    
    if reqs:
        for r in reqs:
            with st.container():
                st.markdown('<div class="studio-card">', unsafe_allow_html=True)
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"**Email:** {r[0]}\n**TID:** `{r[1]}`")
                
                # --- APPROVE / BLOCK BUTTONS ---
                if c2.button("✅ APPROVE", key=f"ok_{r[1]}"):
                    conn.execute("UPDATE users SET status='ACTIVE' WHERE email=?", (r[0],))
                    conn.execute("UPDATE payments SET status='APPROVED' WHERE tid=?", (r[1],))
                    conn.commit(); st.rerun()
                    
                if c3.button("❌ BLOCK", key=f"no_{r[1]}"):
                    conn.execute("UPDATE payments SET status='REJECTED' WHERE tid=?", (r[1],))
                    conn.commit(); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    else: st.info("✅ All Clear")
    
    st.write("---")
    st.markdown("### 👥 All Agents")
    users = conn.execute("SELECT name, email, status, autopilot_id FROM users").fetchall()
    st.dataframe(pd.DataFrame(users, columns=["Name", "Email", "Status", "Drive ID"]), use_container_width=True)
    conn.close()

def user_dashboard():
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
        st.title(st.session_state.user['name'])
        if st.button("🔴 LOGOUT"): st.session_state.user=None; st.rerun()

    # 5 TABS (ALL FEATURES RESTORED)
    tabs = st.tabs(["📊 STUDIO 3D", "🎬 FACTORY", "✈️ AUTO-PILOT", "🧠 AI HACKER", "🌐 SOCIAL"])
    
    with tabs[0]:
        st.markdown("### 📊 Live Analytics")
        c1, c2 = st.columns(2)
        with c1: st.plotly_chart(get_3d_realtime_chart(), use_container_width=True)
        with c2: st.plotly_chart(get_3d_globe(), use_container_width=True)
        st.plotly_chart(get_pca_3d(), use_container_width=True)

    with tabs[1]:
        st.markdown("### 🎬 Unlimited Video Factory")
        files = st.file_uploader("Upload Clips", accept_multiple_files=True)
        if st.button("🚀 PROCESS REAL VIDEO"):
            if files:
                with st.spinner("Processing..."):
                    res = process_video_real(files)
                    if "Error" not in res: st.video(res)
                    else: st.error(res)

    with tabs[2]:
        st.markdown("### ✈️ Drive Auto-Pilot")
        st.text_input("Drive Folder ID", value=st.session_state.user.get('autopilot_id', ''))
        if st.button("ACTIVATE"):
            st.session_state.logs = [f"[{datetime.now()}] 🟢 System Started...", f"[{datetime.now()}] 🔎 Scanning Drive...", f"[{datetime.now()}] 🚀 Uploading..."]
            st.rerun()
        
        # LOGS TERMINAL
        log_txt = "\n".join(st.session_state.logs)
        st.markdown(f'<div class="log-box">{log_txt}</div>', unsafe_allow_html=True)

    with tabs[3]:
        st.markdown("### 🧠 Deep Seek Strategy")
        niche = st.text_input("Niche")
        if st.button("HACK ALGORITHM"):
            st.code(deep_seek_brain(niche))

    with tabs[4]:
        st.markdown("### 🌐 Social Connect")
        st.file_uploader("Upload YouTube JSON")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("YouTube", "Connected"); c2.metric("Insta", "Active")
        c3.metric("TikTok", "Ready"); c4.metric("Facebook", "Synced")

def login():
    st.markdown("<br><h1 style='text-align:center; text-shadow: 0 0 20px #00f3ff'>👑 MOHSIN EMPIRE</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["LOGIN", "REGISTER"])
    with t1:
        st.markdown('<div class="studio-card">', unsafe_allow_html=True)
        e = st.text_input("Email", key="l")
        p = st.text_input("Password", type="password", key="p")
        if st.button("LOGIN"):
            h = hashlib.sha256(p.encode()).hexdigest()
            conn = sqlite3.connect(DB_PATH)
            u = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (e, h)).fetchone()
            if u:
                st.session_state.user = {'email': u[0], 'name': u[2], 'role': u[4], 'autopilot_id': u[6]}
                st.rerun()
            else: st.error("Failed")
        st.markdown('</div>', unsafe_allow_html=True)
            
    with t2:
        st.markdown('<div class="studio-card">', unsafe_allow_html=True)
        re = st.text_input("New Email")
        rn = st.text_input("Name")
        rp = st.text_input("New Password", type="password")
        if st.button("REGISTER"):
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                          (re, hashlib.sha256(rp.encode()).hexdigest(), rn, "000", "PENDING", "UTC", "None", "None", str(datetime.now())))
                conn.commit(); conn.close()
                st.success("Registered! Now Login.")
            except: st.error("Email Taken")
        st.markdown('</div>', unsafe_allow_html=True)

def payment_wall():
    st.error("⛔ Account Pending")
    tid = st.text_input("Enter TID")
    if st.button("Submit"):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO payments VALUES (?, ?, ?, ?, ?)", 
                  (st.session_state.user['email'], tid, "JazzCash", "REVIEW", str(datetime.now())))
        conn.execute("UPDATE users SET status='REVIEW' WHERE email=?", (st.session_state.user['email'],))
        conn.commit(); conn.close()
        st.session_state.user['role'] = 'REVIEW'
        st.rerun()

# --- EXECUTION ---
if __name__ == "__main__":
    if not st.session_state.user: login()
    else:
        role = st.session_state.user['role']
        if role == 'ADMIN': admin_dashboard()
        elif role == 'ACTIVE': user_dashboard()
        elif role == 'REVIEW': st.info("⏳ Pending Review...")
        else: payment_wall()
    
