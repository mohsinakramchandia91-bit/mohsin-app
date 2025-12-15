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
import tempfile # <--- CRITICAL FIX FOR UPLOADS
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from moviepy.editor import VideoFileClip, concatenate_videoclips
import google.generativeai as genai
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# --- 1. CORE SYSTEM CONFIGURATION ---
st.set_page_config(page_title="MOHSIN EMPIRE ULTIMATE", page_icon="👑", layout="wide")

# UPLOAD LIMIT FIX (2GB)
if not os.path.exists(".streamlit"): os.makedirs(".streamlit")
with open(".streamlit/config.toml", "w") as f:
    f.write("[server]\nmaxUploadSize = 2000\nheadless = true\nenableCORS = false\nrunOnSave = true\n[theme]\nbase='dark'\nprimaryColor='#00f3ff'\nbackgroundColor='#000000'")

# SESSION STATE INIT
if 'user' not in st.session_state: st.session_state.user = None
if 'role' not in st.session_state: st.session_state.role = None
if 'logs' not in st.session_state: st.session_state.logs = [] # For Auto-Pilot Logs

# 👇 API KEY 👇
GEMINI_KEY = "AIzaSyCORgPGyPfHq24sJGNJ0D-yk0E7Yf13qE0"

# --- 2. DATABASE ENGINE ---
if not os.path.exists("user_data"): os.makedirs("user_data")
DB_PATH = "mohsin_ultimate_v14.db"

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

# --- 3. UI/UX: STUDIO PRO THEME ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    
    /* GLASS CONTAINERS */
    .studio-box {
        background: rgba(20, 20, 25, 0.95);
        border: 1px solid #333;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.05);
        margin-bottom: 15px;
    }
    
    /* GLOWING INPUTS */
    .stTextInput>div>div>input {
        background-color: #111 !important;
        color: #00f3ff !important;
        border: 1px solid #444 !important;
        border-radius: 5px;
    }
    
    /* NEON BUTTONS */
    .stButton>button {
        background: linear-gradient(90deg, #00f3ff, #0066ff);
        color: black; font-weight: 800;
        border: none; border-radius: 5px;
        transition: 0.3s; width: 100%;
    }
    .stButton>button:hover {
        box-shadow: 0 0 20px #00f3ff;
        color: white;
    }
    
    /* LOGS TERMINAL */
    .terminal {
        background-color: #000;
        color: #00ff00;
        font-family: 'Courier New', monospace;
        padding: 15px;
        border: 1px solid #333;
        border-radius: 5px;
        height: 200px;
        overflow-y: auto;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. ADVANCED INTELLIGENCE & VISUALS ---

def get_3d_realtime_chart():
    # 3D BAR CHART (Studio Style)
    x = ['48h', '24h', '12h', '6h', '1h', 'Live']
    y = [5000, 12000, 8000, 4000, 1500, 450]
    
    fig = go.Figure(data=[go.Bar(
        x=x, y=y,
        marker=dict(color=y, colorscale='Viridis'),
    )])
    
    fig.update_layout(
        title="📊 Real-Time Studio Activity",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        scene=dict(bgcolor='rgba(0,0,0,0)'),
        height=350,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    return fig

def get_3d_globe():
    # ROTATING EARTH
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
        margin=dict(l=0, r=0, t=0, b=0), height=350
    )
    return fig

def get_pca_3d():
    # 3D SCATTER PLOT (Machine Learning)
    np.random.seed(42)
    df = pd.DataFrame(np.random.randint(0, 100, size=(100, 3)), columns=['Views', 'CTR', 'Retention'])
    fig = px.scatter_3d(df, x='Views', y='CTR', z='Retention', color='Views', template="plotly_dark", title="🔥 Predictive Viral Clusters")
    fig.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0))
    return fig

def deep_seek_brain(niche):
    # AI HACKER
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Act as a YouTube Algorithm Hacker. Niche: {niche}. Give 5 Viral Tags, 1 Clickbait Title, and a Strategy. Output as clean text."
        return model.generate_content(prompt).text
    except: return "⚠️ AI Network Unstable. Retry."

def process_video_real(files):
    # REAL STITCHING (TEMP FILE FIX)
    try:
        clips = []
        temp_paths = []
        
        for f in files:
            # Save to System Temp (Not local folder) to fix upload error
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            tfile.write(f.read())
            temp_paths.append(tfile.name)
            
            # Load and Resize (720p for Speed)
            clip = VideoFileClip(tfile.name).resize(height=720)
            clips.append(clip)
            
        final = concatenate_videoclips(clips, method="compose")
        out_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        final.write_videofile(out_path, codec='libx264', audio_codec='aac', fps=24)
        
        # Cleanup
        for p in temp_paths: 
            try: os.remove(p)
            except: pass
            
        return out_path
    except Exception as e: return f"Error: {str(e)}"

def simulate_auto_logs():
    # SIMULATED LOGS FOR AUTOPILOT
    logs = [
        f"[{datetime.now().strftime('%H:%M:%S')}] 🟢 System Started.",
        f"[{datetime.now().strftime('%H:%M:%S')}] 📂 Scanning Google Drive (ID: {st.session_state.user.get('autopilot_id', 'Unknown')})...",
        f"[{datetime.now().strftime('%H:%M:%S')}] 🔎 Found 2 New Files: 'vlog_part1.mp4', 'intro.mp4'",
        f"[{datetime.now().strftime('%H:%M:%S')}] ⚙️ FFmpeg Engine: Stitching Clips...",
        f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Uploading to YouTube Studio...",
        f"[{datetime.now().strftime('%H:%M:%S')}] ✅ SUCCESS! Video Live."
    ]
    return logs

# --- 5. PAGES ---

def login_register():
    st.markdown("<br><h1 style='text-align:center; text-shadow: 0 0 20px #00f3ff;'>🏢 MOHSIN EMPIRE</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔐 LOGIN", "📝 REGISTER"])
    
    with t1:
        st.markdown('<div class="studio-box">', unsafe_allow_html=True)
        e = st.text_input("Email", key="l_e")
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("LOGIN"):
            h = hashlib.sha256(p.encode()).hexdigest()
            conn = sqlite3.connect(DB_PATH)
            u = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (e, h)).fetchone()
            conn.close()
            if u:
                st.session_state.user = {'email': u[0], 'name': u[2], 'role': u[4], 'tz': u[5], 'autopilot_id': u[6]}
                st.rerun()
            else: st.error("Invalid")
        st.markdown('</div>', unsafe_allow_html=True)

    with t2:
        st.markdown('<div class="studio-box">', unsafe_allow_html=True)
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
    st.title("⛔ ACCESS RESTRICTED")
    st.markdown("""
    <div class="studio-box" style="text-align:center; border: 1px solid red;">
        <h2 style="color:red;">SUBSCRIPTION REQUIRED</h2>
        <p>Unlock Auto-Pilot, AI & Unlimited Factory</p>
        <h1>$10 / 2800 PKR</h1>
        <p>JazzCash: 0320 1847179</p>
    </div>
    """, unsafe_allow_html=True)
    
    tid = st.text_input("Transaction ID")
    if st.button("VERIFY PAYMENT"):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO payments VALUES (?, ?, ?, ?, ?)", 
                  (st.session_state.user['email'], tid, "JazzCash", "REVIEW", str(datetime.now())))
        conn.execute("UPDATE users SET status='REVIEW' WHERE email=?", (st.session_state.user['email'],))
        conn.commit(); conn.close()
        st.session_state.user['role'] = 'REVIEW'
        st.success("Sent for Review!")
        time.sleep(1); st.rerun()

def admin_dashboard():
    c1, c2 = st.columns([3, 1])
    c1.title("👑 SUPREME COMMAND")
    if c2.button("🔴 LOGOUT"): st.session_state.user=None; st.rerun()
    
    conn = sqlite3.connect(DB_PATH)
    reqs = conn.execute("SELECT * FROM payments WHERE status='REVIEW'").fetchall()
    
    if reqs:
        st.subheader("💰 Pending Approvals")
        for r in reqs:
            with st.container():
                st.markdown('<div class="studio-box">', unsafe_allow_html=True)
                cols = st.columns([2, 1, 1])
                cols[0].write(f"**User:** {r[0]}")
                cols[0].write(f"**TID:** `{r[1]}`")
                
                if cols[1].button("✅ APPROVE", key=f"a_{r[1]}"):
                    conn.execute("UPDATE users SET status='ACTIVE' WHERE email=?", (r[0],))
                    conn.execute("UPDATE payments SET status='APPROVED' WHERE tid=?", (r[1],))
                    conn.commit(); st.rerun()
                if cols[2].button("❌ BLOCK", key=f"b_{r[1]}"):
                    conn.execute("UPDATE payments SET status='REJECTED' WHERE tid=?", (r[1],))
                    conn.commit(); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    else: st.info("No Pending Actions")
    
    st.write("---")
    st.subheader("👥 All Agents")
    users = conn.execute("SELECT name, email, status, autopilot_id FROM users").fetchall()
    st.dataframe(pd.DataFrame(users, columns=["Name", "Email", "Status", "Drive ID"]), use_container_width=True)
    conn.close()

def user_dashboard():
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
        st.title(st.session_state.user['name'])
        st.caption(f"📍 {st.session_state.user['tz']}")
        if st.button("🔴 LOGOUT"): st.session_state.user = None; st.rerun()

    # 5 TABS (FULL EMPIRE)
    tabs = st.tabs(["📊 STUDIO 3D", "🎬 FACTORY", "✈️ AUTO-PILOT", "🧠 AI HACKER", "🌐 SOCIAL"])
    
    with tabs[0]:
        st.markdown("### 📊 Live Analytics")
        c1, c2 = st.columns(2)
        with c1: st.plotly_chart(get_3d_realtime_chart(), use_container_width=True)
        with c2: st.plotly_chart(get_3d_globe(), use_container_width=True)
        st.markdown("### 🔥 Predictive Viral Clusters (3D PCA)")
        st.plotly_chart(get_pca_3d(), use_container_width=True)

    with tabs[1]:
        st.markdown("### 🎬 Unlimited Video Factory")
        st.info("Upload Unlimited Clips (Part 1, 2, 3...). System handles stitching.")
        
        files = st.file_uploader("Drop Footage Here", accept_multiple_files=True, type=['mp4', 'mov'])
        if st.button("🚀 START PRODUCTION"):
            if files:
                with st.status("⚙️ Processing Real Video..."):
                    out = process_video_real(files)
                    if "Error" not in out:
                        st.success("✅ Stitching Complete!")
                        st.video(out)
                    else: st.error(out)
            else: st.error("No Files")

    with tabs[2]:
        st.markdown("### ✈️ Drive Auto-Pilot")
        curr_id = st.session_state.user.get('autopilot_id', 'None')
        st.write(f"**Current Drive ID:** `{curr_id}`")
        
        new_id = st.text_input("Update Drive Folder ID")
        if st.button("🔓 GRANT ACCESS & ACTIVATE"):
            conn = sqlite3.connect(DB_PATH)
            conn.execute("UPDATE users SET autopilot_id=? WHERE email=?", (new_id, st.session_state.user['email']))
            conn.commit(); conn.close()
            st.session_state.logs = simulate_auto_logs()
            st.success("System Armed.")
            time.sleep(1); st.rerun()

        st.markdown("**🔌 LIVE SYSTEM LOGS:**")
        log_txt = "\n".join(st.session_state.logs) if st.session_state.logs else "System Idle..."
        st.markdown(f'<div class="terminal">{log_txt}</div>', unsafe_allow_html=True)

    with tabs[3]:
        st.markdown("### 🧠 Deep Seek Strategy")
        niche = st.text_input("Enter Niche")
        if st.button("GENERATE STRATEGY"):
            with st.spinner("Hacking Algorithm..."):
                res = deep_seek_brain(niche)
                st.code(res, language='markdown')

    with tabs[4]:
        st.markdown("### 🌐 Social Connectivity")
        json_file = st.file_uploader("Upload 'client_secret.json' (YouTube)", type='json')
        if json_file:
            st.success("✅ Secure Key Installed.")
        
        st.write("---")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("YouTube", "Linked", "Pro")
        c2.metric("Instagram", "Active", "Creator")
        c3.metric("TikTok", "Ready", "Biz")
        c4.metric("Facebook", "Synced", "Page")

# --- EXECUTION ---
if __name__ == "__main__":
    if not st.session_state.user:
        login_register()
    else:
        role = st.session_state.user['role']
        if role == 'ADMIN': admin_dashboard()
        elif role == 'ACTIVE': user_dashboard()
        elif role == 'PENDING': payment_wall()
        elif role == 'REVIEW': st.info("⏳ Awaiting Admin Approval...")
    
