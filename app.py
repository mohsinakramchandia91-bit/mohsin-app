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

# --- 1. CONFIG ---
st.set_page_config(page_title="MOHSIN EMPIRE V17", page_icon="👑", layout="wide")

# UPLOAD FIX
if not os.path.exists(".streamlit"): os.makedirs(".streamlit")
with open(".streamlit/config.toml", "w") as f:
    f.write("[server]\nmaxUploadSize = 2000\nheadless = true\nenableCORS = false\nrunOnSave = true\n[theme]\nbase='dark'\nprimaryColor='#00f3ff'\nbackgroundColor='#000000'")

# STATE
if 'user' not in st.session_state: st.session_state.user = None
if 'logs' not in st.session_state: st.session_state.logs = []

# API KEY
GEMINI_KEY = "AIzaSyCORgPGyPfHq24sJGNJ0D-yk0E7Yf13qE0"

# --- 2. DATABASE ---
if not os.path.exists("user_data"): os.makedirs("user_data")
DB_PATH = "mohsin_final_v17.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (email TEXT PRIMARY KEY, password TEXT, name TEXT, phone TEXT, status TEXT, 
                  timezone TEXT, autopilot_id TEXT, yt_json TEXT, joined_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS payments 
                 (email TEXT, tid TEXT, method TEXT, status TEXT, date TEXT)''')
    
    # SUPER ADMIN
    try:
        admin_pass = hashlib.sha256("Mohsin5577@".encode()).hexdigest()
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                 ("mohsinakramchandia91@gmail.com", admin_pass, "CEO MOHSIN", "03201847179", 
                  "ADMIN", "Asia/Karachi", "None", "Connected", str(datetime.now())))
    except: pass
    conn.commit(); conn.close()

init_db()

# --- 3. UI STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #000; color: #fff; }
    .glass-card {
        background: rgba(20, 30, 40, 0.9);
        border: 1px solid #333; border-radius: 10px;
        padding: 15px; margin-bottom: 10px;
    }
    .stButton>button {
        width: 100%; border-radius: 5px; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. VISUALS ---
def get_globe():
    df = pd.DataFrame({"Country": ["Pak", "USA"], "Z": [100, 200], "Code": ["PAK", "USA"]})
    fig = go.Figure(data=go.Choropleth(locations=df['Code'], z=df['Z'], colorscale='Viridis'))
    fig.update_layout(geo=dict(showframe=False, projection_type='orthographic', bgcolor='rgba(0,0,0,0)'),
                      paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=0, b=0), height=300)
    return fig

def get_pca():
    df = pd.DataFrame(np.random.randint(0,100,size=(50, 3)), columns=['A','B','C'])
    return px.scatter_3d(df, x='A', y='B', z='C', color='A', template="plotly_dark", height=300)

def deep_seek(niche):
    try:
        genai.configure(api_key=GEMINI_KEY)
        return genai.GenerativeModel('gemini-1.5-flash').generate_content(f"Strategy for {niche}").text
    except: return "Connecting..."

# --- 5. FACTORY ---
def process_real(files):
    try:
        clips = []
        temps = []
        for f in files:
            t = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            t.write(f.read())
            temps.append(t.name)
            clips.append(VideoFileClip(t.name).resize(height=480))
        final = concatenate_videoclips(clips, method="compose")
        out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        final.write_videofile(out, codec='libx264', fps=24, preset='ultrafast')
        for p in temps: os.remove(p)
        return out
    except Exception as e: return str(e)

# --- 6. PAGES ---

def admin_dashboard():
    st.title("👑 SUPREME COMMAND")
    if st.button("🔴 LOGOUT"): st.session_state.user=None; st.rerun()
    
    conn = sqlite3.connect(DB_PATH)
    
    # --- HERE IS THE FIX: BUTTONS FOR EVERYONE ---
    st.markdown("### 👥 Manage All Agents")
    
    # Fetch ALL users except Admin
    users = conn.execute("SELECT name, email, status FROM users WHERE status != 'ADMIN'").fetchall()
    
    if users:
        for u in users:
            with st.container():
                st.markdown(f'<div class="glass-card">', unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
                
                c1.write(f"👤 **{u[0]}**")
                c2.write(f"📧 {u[1]}")
                
                # Show Status Color
                if u[2] == "ACTIVE": c2.success("ACTIVE")
                elif u[2] == "PENDING": c2.warning("PENDING")
                elif u[2] == "REVIEW": c2.info("REVIEW")
                else: c2.error("BLOCKED")

                # FORCE BUTTONS (DIRECT CONTROL)
                if c3.button("✅ ACTIVATE", key=f"act_{u[1]}"):
                    conn.execute("UPDATE users SET status='ACTIVE' WHERE email=?", (u[1],))
                    conn.execute("UPDATE payments SET status='APPROVED' WHERE email=?", (u[1],)) # Auto approve payment if exists
                    conn.commit()
                    st.toast(f"{u[0]} Activated!"); time.sleep(1); st.rerun()
                
                if c4.button("❌ DELETE", key=f"del_{u[1]}"):
                    conn.execute("DELETE FROM users WHERE email=?", (u[1],))
                    conn.execute("DELETE FROM payments WHERE email=?", (u[1],))
                    conn.commit()
                    st.toast(f"{u[0]} Deleted!"); time.sleep(1); st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No Users Found.")
        
    conn.close()

def user_dashboard():
    with st.sidebar:
        st.title(st.session_state.user['name'])
        if st.button("🔴 LOGOUT"): st.session_state.user=None; st.rerun()

    tabs = st.tabs(["📊 3D STUDIO", "🎬 FACTORY", "✈️ AUTOPILOT", "🧠 AI", "🌐 SOCIAL"])
    
    with tabs[0]:
        c1, c2 = st.columns(2)
        with c1: st.plotly_chart(get_globe(), use_container_width=True)
        with c2: st.plotly_chart(get_pca(), use_container_width=True)

    with tabs[1]:
        files = st.file_uploader("Upload", accept_multiple_files=True)
        if st.button("🚀 Process"):
            res = process_real(files)
            if "Error" not in res: st.video(res)
            else: st.error(res)

    with tabs[2]:
        st.info("Logs Active")
        st.code("[System] Monitoring Drive...")

    with tabs[3]:
        n = st.text_input("Niche")
        if st.button("HACK"): st.write(deep_seek(n))

    with tabs[4]:
        st.file_uploader("YouTube JSON")
        st.success("Socials Ready")

def login():
    st.markdown("<br><h1 style='text-align:center'>🏢 MOHSIN EMPIRE</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["LOGIN", "REGISTER"])
    with t1:
        e = st.text_input("Email", key="l")
        p = st.text_input("Pass", type="password", key="p")
        if st.button("LOGIN"):
            h = hashlib.sha256(p.encode()).hexdigest()
            conn = sqlite3.connect(DB_PATH)
            u = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (e, h)).fetchone()
            if u:
                st.session_state.user = {'email': u[0], 'name': u[2], 'role': u[4]}
                st.rerun()
            else: st.error("Invalid")
    with t2:
        re = st.text_input("Email")
        rn = st.text_input("Name")
        rp = st.text_input("Pass", type="password")
        if st.button("REGISTER"):
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                          (re, hashlib.sha256(rp.encode()).hexdigest(), rn, "000", "PENDING", "UTC", "None", "None", str(datetime.now())))
                conn.commit(); conn.close()
                st.success("Registered!")
            except: st.error("Exists")

def payment_wall():
    st.error("Account Pending")
    tid = st.text_input("TID")
    if st.button("Submit"):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO payments VALUES (?, ?, ?, ?, ?)", 
                  (st.session_state.user['email'], tid, "Jazz", "REVIEW", str(datetime.now())))
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
        else: payment_wall()

