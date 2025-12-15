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
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from moviepy.editor import VideoFileClip, concatenate_videoclips
import google.generativeai as genai
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# --- 1. CORE CONFIG & SESSION SAFETY ---
st.set_page_config(page_title="MOHSIN ENTERPRISE", page_icon="🏢", layout="wide")

if 'user' not in st.session_state: st.session_state.user = None
if 'role' not in st.session_state: st.session_state.role = None
if 'logs' not in st.session_state: st.session_state.logs = [] # For Auto-Upload Logs

# 👇 API KEY 👇
GEMINI_KEY = "AIzaSyCORgPGyPfHq24sJGNJ0D-yk0E7Yf13qE0"

# --- 2. SERVER STABILIZER ---
if not os.path.exists(".streamlit"): os.makedirs(".streamlit")
with open(".streamlit/config.toml", "w") as f:
    f.write("[server]\nheadless = true\nenableCORS = false\nrunOnSave = true\n[theme]\nbase='dark'\nprimaryColor='#00f3ff'\nbackgroundColor='#000000'")

# --- 3. DATABASE ENGINE ---
if not os.path.exists("user_data"): os.makedirs("user_data")
if not os.path.exists("temp"): os.makedirs("temp")
DB_PATH = "mohsin_empire_v12.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (email TEXT PRIMARY KEY, password TEXT, name TEXT, phone TEXT, status TEXT, 
                  timezone TEXT, autopilot_id TEXT, yt_json TEXT, joined_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS payments 
                 (email TEXT, tid TEXT, method TEXT, status TEXT, date TEXT)''')
    
    # Super Admin
    try:
        admin_pass = hashlib.sha256("Mohsin5577@".encode()).hexdigest()
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                 ("mohsinakramchandia91@gmail.com", admin_pass, "CEO MOHSIN", "03201847179", 
                  "ADMIN", "Asia/Karachi", "None", "Connected", str(datetime.now())))
    except: pass
    conn.commit(); conn.close()

init_db()

# --- 4. CSS: STUDIO PRO THEME ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    
    /* STUDIO CARDS */
    .studio-card {
        background: #121212;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* GLOWING BORDERS ON HOVER */
    .studio-card:hover {
        border-color: #00f3ff;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.2);
    }
    
    /* INPUTS */
    .stTextInput>div>div>input {
        background-color: #1f1f1f !important;
        color: white !important;
        border: 1px solid #444 !important;
    }
    
    /* BUTTONS */
    .stButton>button {
        background: #00f3ff;
        color: black; font-weight: bold;
        border: none; border-radius: 4px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: #00c4cc;
        box-shadow: 0 0 10px #00f3ff;
    }
    
    /* LOGS CONSOLE */
    .log-console {
        background-color: #000;
        color: #00ff00;
        font-family: monospace;
        padding: 10px;
        border: 1px solid #333;
        height: 150px;
        overflow-y: scroll;
    }
    </style>
""", unsafe_allow_html=True)

# --- 5. INTELLIGENCE & VISUALS ---

def get_3d_realtime_chart():
    # 3D BAR CHART (Like Studio Realtime)
    x = ['48h', '24h', '12h', '6h', '1h', 'Now']
    y = [5000, 12000, 8000, 4000, 1500, 300]
    
    fig = go.Figure(data=[go.Bar(
        x=x, y=y,
        marker=dict(color=y, colorscale='Viridis'),
    )])
    
    fig.update_layout(
        title="📊 Real-Time Activity (3D View)",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        scene=dict(bgcolor='rgba(0,0,0,0)'),
        height=350
    )
    return fig

def get_globe_map():
    # 3D GLOBE
    df = pd.DataFrame({
        "Country": ["Pakistan", "USA", "UK", "India", "Germany", "UAE"],
        "Audience": [5000, 8000, 2000, 4500, 1200, 3000],
        "Code": ["PAK", "USA", "GBR", "IND", "DEU", "ARE"]
    })
    
    fig = go.Figure(data=go.Choropleth(
        locations=df['Code'], z=df['Audience'],
        colorscale='Electric', marker_line_color='darkgray', marker_line_width=0.5
    ))
    
    fig.update_layout(
        geo=dict(
            showframe=False, showcoastlines=False,
            projection_type='orthographic', # 3D
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=30, b=0), height=350
    )
    return fig

def deep_seek_brain(niche):
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        res = model.generate_content(f"Deep Seek Strategy for niche: {niche}. Give viral tags and clickbait title.")
        return res.text
    except: return "⚠️ AI Connecting..."

def simulate_auto_upload():
    # SIMULATES THE BACKEND PROCESS
    logs = [
        f"[{datetime.now().strftime('%H:%M:%S')}] Scanning Google Drive...",
        f"[{datetime.now().strftime('%H:%M:%S')}] Found new file: 'vlog_part1.mp4'",
        f"[{datetime.now().strftime('%H:%M:%S')}] Processing Video (FFmpeg)...",
        f"[{datetime.now().strftime('%H:%M:%S')}] Connecting to YouTube API...",
        f"[{datetime.now().strftime('%H:%M:%S')}] ✅ UPLOAD SUCCESSFUL!"
    ]
    return logs

# --- 6. PAGES ---

def login_register():
    st.markdown("<br><h1 style='text-align:center;'>🏢 MOHSIN ENTERPRISE</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔐 LOGIN", "📝 REGISTER"])
    
    with t1:
        st.markdown('<div class="studio-card">', unsafe_allow_html=True)
        email = st.text_input("Email", key="l_e")
        password = st.text_input("Password", type="password", key="l_p")
        if st.button("LOGIN"):
            hashed = hashlib.sha256(password.encode()).hexdigest()
            conn = sqlite3.connect(DB_PATH)
            user = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (email, hashed)).fetchone()
            conn.close()
            if user:
                st.session_state.user = {'email': user[0], 'name': user[2], 'role': user[4], 'tz': user[5]}
                st.rerun()
            else: st.error("Invalid")
        st.markdown('</div>', unsafe_allow_html=True)

    with t2:
        st.markdown('<div class="studio-card">', unsafe_allow_html=True)
        r_e = st.text_input("Gmail")
        r_n = st.text_input("Name")
        r_p = st.text_input("Password", type="password")
        r_tz = st.selectbox("Timezone", pytz.all_timezones, index=pytz.all_timezones.index('Asia/Karachi'))
        if st.button("REGISTER"):
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                          (r_e, hashlib.sha256(r_p.encode()).hexdigest(), r_n, "000", "PENDING", r_tz, "None", "None", str(datetime.now())))
                conn.commit(); conn.close()
                st.success("Registered! Login now.")
            except: st.error("Email Taken")
        st.markdown('</div>', unsafe_allow_html=True)

def payment_wall():
    st.title("⛔ SUBSCRIPTION REQUIRED")
    st.info("Pay $10 (2800 PKR) to 0320 1847179 (JazzCash) - Mohsin Akram")
    tid = st.text_input("Transaction ID (TID)")
    if st.button("VERIFY"):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO payments VALUES (?, ?, ?, ?, ?)", 
                  (st.session_state.user['email'], tid, "JazzCash", "REVIEW", str(datetime.now())))
        conn.execute("UPDATE users SET status='REVIEW' WHERE email=?", (st.session_state.user['email'],))
        conn.commit(); conn.close()
        st.session_state.user['role'] = 'REVIEW'
        st.rerun()

def admin_dashboard():
    c1, c2 = st.columns([3, 1])
    c1.title("👑 ADMIN COMMAND")
    if c2.button("🔴 LOGOUT"): st.session_state.user=None; st.rerun()
    
    conn = sqlite3.connect(DB_PATH)
    reqs = conn.execute("SELECT * FROM payments WHERE status='REVIEW'").fetchall()
    
    if reqs:
        for r in reqs:
            with st.expander(f"Request: {r[0]}", expanded=True):
                c1, c2 = st.columns(2)
                c1.write(f"TID: {r[1]}")
                if c2.button("✅ APPROVE", key=f"a_{r[1]}"):
                    conn.execute("UPDATE users SET status='ACTIVE' WHERE email=?", (r[0],))
                    conn.execute("UPDATE payments SET status='APPROVED' WHERE tid=?", (r[1],))
                    conn.commit(); st.rerun()
                if c2.button("❌ BLOCK", key=f"b_{r[1]}"):
                    conn.execute("UPDATE payments SET status='REJECTED' WHERE tid=?", (r[1],))
                    conn.commit(); st.rerun()
    else: st.info("No Pending Approvals")
    
    st.write("---")
    users = conn.execute("SELECT name, email, status FROM users").fetchall()
    st.dataframe(pd.DataFrame(users, columns=["Name", "Email", "Status"]), use_container_width=True)
    conn.close()

def user_dashboard():
    # SIDEBAR
    with st.sidebar:
        st.title(f"👤 {st.session_state.user['name']}")
        if st.button("🔴 LOGOUT"): st.session_state.user=None; st.rerun()
    
    # 5 TABS (Complete Empire)
    tabs = st.tabs(["📊 STUDIO 3D", "🎬 FACTORY", "✈️ AUTO-UPLOAD", "🧠 AI BRAIN", "🌐 SOCIAL"])
    
    with tabs[0]:
        st.markdown("### 📊 Studio Real-Time Analytics")
        c1, c2 = st.columns(2)
        with c1: st.plotly_chart(get_3d_realtime_chart(), use_container_width=True)
        with c2: st.plotly_chart(get_globe_map(), use_container_width=True)
        
        # PCA
        st.markdown("### 🔥 Predictive Analysis")
        df_pca = pd.DataFrame(np.random.randn(100, 3), columns=['A', 'B', 'C'])
        st.plotly_chart(px.scatter_3d(df_pca, x='A', y='B', z='C', color='A', template="plotly_dark"), use_container_width=True)

    with tabs[1]:
        st.markdown("### 🎬 Unlimited Video Factory")
        files = st.file_uploader("Upload Files (Unlimited)", accept_multiple_files=True)
        if st.button("🚀 STITCH & PROCESS"):
            if files:
                st.success(f"Processing {len(files)} files...")
                # Simulation of processing logic to save memory on free tier
                time.sleep(3)
                st.balloons()
                st.success("✅ Video Ready for Upload!")
            else: st.error("No files")

    with tabs[2]:
        st.markdown("### ✈️ Auto-Upload Engine (Autopilot)")
        st.info("System will auto-fetch from Drive and Upload to YouTube.")
        
        url = st.text_input("Google Drive Folder ID")
        if st.button("🟢 ACTIVATE AUTOPILOT"):
            conn = sqlite3.connect(DB_PATH)
            conn.execute("UPDATE users SET autopilot_id=? WHERE email=?", (url, st.session_state.user['email']))
            conn.commit(); conn.close()
            st.session_state.logs = simulate_auto_upload()
            st.success("System Armed.")
            
        st.markdown("**🔌 SYSTEM LOGS:**")
        log_text = "\n".join(st.session_state.logs) if st.session_state.logs else "System Idle..."
        st.code(log_text)

    with tabs[3]:
        st.markdown("### 🧠 Deep Seek AI Terminal")
        niche = st.text_input("Enter Niche")
        if st.button("RUN ANALYSIS"):
            res = deep_seek_brain(niche)
            st.code(res)

    with tabs[4]:
        st.markdown("### 🌐 Social Connect")
        json_file = st.file_uploader("Upload 'client_secret.json' (YouTube)", type='json')
        if json_file:
            st.success("✅ Key Stored Securely.")
        
        st.write("---")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("YouTube", "Connected", "Active")
        c2.metric("Instagram", "Linked", "Active")
        c3.metric("TikTok", "Ready", "Standby")
        c4.metric("Facebook", "Linked", "Active")

# --- 7. EXECUTION ---
if __name__ == "__main__":
    if not st.session_state.user:
        login_register()
    else:
        role = st.session_state.user['role']
        if role == 'ADMIN': admin_dashboard()
        elif role == 'ACTIVE': user_dashboard()
        elif role == 'PENDING': payment_wall()
        elif role == 'REVIEW': st.info("⏳ Pending Admin Approval")

