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
from apscheduler.schedulers.background import BackgroundScheduler
from moviepy.editor import VideoFileClip, concatenate_videoclips

# --- CONFIG ---
st.set_page_config(page_title="MOHSIN EMPIRE", page_icon="👑", layout="wide")
GEMINI_KEY = "AIzaSyCORgPGyPfHq24sJGNJ0D-yk0E7Yf13qE0"

# --- DATABASE SETUP ---
if not os.path.exists("user_data"): os.makedirs("user_data")
if not os.path.exists("temp"): os.makedirs("temp")
DB_PATH = "mohsin_admin_fix.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (email TEXT PRIMARY KEY, password TEXT, name TEXT, phone TEXT, status TEXT, 
                  joined_date TEXT)''')
    # Payments Table
    c.execute('''CREATE TABLE IF NOT EXISTS payments 
                 (email TEXT, tid TEXT, proof TEXT, status TEXT, date TEXT)''')
    
    # Auto-Create Admin
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", 
                 ("mohsinakramchandia91@gmail.com", hashlib.sha256("Mohsin5577@".encode()).hexdigest(), 
                  "SUPER ADMIN", "03201847179", "ADMIN", str(datetime.now())))
    except: pass
    conn.commit(); conn.close()

init_db()

# --- CSS: PRO ADMIN THEME ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    
    /* ADMIN CARDS */
    .admin-card {
        background: #1f2937; border: 1px solid #374151;
        padding: 15px; border-radius: 10px; margin-bottom: 10px;
    }
    
    /* BUTTONS */
    .stButton>button {
        width: 100%; border-radius: 5px; font-weight: bold;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #00f3ff; border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- BACKEND FUNCTIONS ---
def process_video_logic(files):
    try:
        clips = []
        for f in files:
            path = f"temp/{f.name}"
            with open(path, "wb") as t: t.write(f.getbuffer())
            clips.append(VideoFileClip(path))
        final = concatenate_videoclips(clips, method="compose")
        out = f"temp/final_{int(time.time())}.mp4"
        final.write_videofile(out, codec='libx264', audio_codec='aac')
        return out
    except: return None

def ai_brain(prompt):
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(prompt).text
    except: return "AI Sleeping..."

# --- PAGES ---

def login_page():
    st.markdown("<br><h1 style='text-align:center; color:#00f3ff;'>💎 MOHSIN EMPIRE</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        tab1, tab2 = st.tabs(["LOGIN", "REGISTER"])
        with tab1:
            em = st.text_input("Email", key="l_em")
            pw = st.text_input("Password", type="password", key="l_pw")
            if st.button("LOGIN"):
                conn = sqlite3.connect(DB_PATH)
                u = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (em, hashlib.sha256(pw.encode()).hexdigest())).fetchone()
                conn.close()
                if u:
                    st.session_state.user = {'email': u[0], 'name': u[2], 'role': u[4]}
                    st.rerun()
                else: st.error("Invalid")
        
        with tab2:
            r_em = st.text_input("Gmail")
            r_nm = st.text_input("Name")
            r_ph = st.text_input("Phone")
            r_pw = st.text_input("Password", type="password")
            if st.button("REGISTER"):
                try:
                    conn = sqlite3.connect(DB_PATH)
                    conn.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", 
                              (r_em, hashlib.sha256(r_pw.encode()).hexdigest(), r_nm, r_ph, "PENDING", str(datetime.now())))
                    conn.commit(); conn.close()
                    st.success("Registered! Login now.")
                except: st.error("Email taken")

def admin_panel():
    st.title("👑 SUPER ADMIN DASHBOARD")
    
    conn = sqlite3.connect(DB_PATH)
    
    # METRICS
    total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    pending = conn.execute("SELECT COUNT(*) FROM users WHERE status='REVIEW'").fetchone()[0]
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Users", total)
    m2.metric("Pending Review", pending)
    m3.metric("System Status", "ONLINE", "Stable")
    
    st.write("---")
    
    # TABS
    tab_pay, tab_users = st.tabs(["💰 PAYMENT REQUESTS", "👥 MANAGE USERS"])
    
    with tab_pay:
        st.subheader("Waiting for Approval")
        # Get users who are in 'REVIEW' status or have payments in 'REVIEW'
        reqs = conn.execute("SELECT * FROM payments WHERE status='REVIEW'").fetchall()
        
        if len(reqs) == 0:
            st.info("✅ No Pending Payments right now.")
        
        for r in reqs:
            with st.expander(f"📩 Request from: {r[0]}", expanded=True):
                c1, c2 = st.columns(2)
                c1.write(f"**TID:** `{r[1]}`")
                c1.write(f"**Date:** {r[4]}")
                
                c2.warning("Action Required:")
                if c2.button("✅ APPROVE ACCESS", key=f"app_{r[1]}"):
                    conn.execute("UPDATE users SET status='ACTIVE' WHERE email=?", (r[0],))
                    conn.execute("UPDATE payments SET status='APPROVED' WHERE tid=?", (r[1],))
                    conn.commit()
                    st.success(f"{r[0]} Activated!")
                    time.sleep(1); st.rerun()
                    
                if c2.button("❌ REJECT / BLOCK", key=f"rej_{r[1]}"):
                    conn.execute("UPDATE payments SET status='REJECTED' WHERE tid=?", (r[1],))
                    conn.commit()
                    st.error("Rejected.")
                    time.sleep(1); st.rerun()

    with tab_users:
        st.subheader("All Registered Users")
        all_users = conn.execute("SELECT name, email, status, phone FROM users").fetchall()
        
        # Show as Dataframe
        df = pd.DataFrame(all_users, columns=["Name", "Email", "Status", "Phone"])
        st.dataframe(df, use_container_width=True)
        
        st.write("### ⚡ Force Action")
        target_email = st.selectbox("Select User to Modify", [u[1] for u in all_users])
        action = st.selectbox("Action", ["ACTIVATE (Free)", "BLOCK", "DELETE"])
        
        if st.button("APPLY ACTION"):
            if action == "ACTIVATE (Free)":
                conn.execute("UPDATE users SET status='ACTIVE' WHERE email=?", (target_email,))
                st.success(f"{target_email} is now ACTIVE!")
            elif action == "BLOCK":
                conn.execute("UPDATE users SET status='BLOCKED' WHERE email=?", (target_email,))
                st.warning("User Blocked.")
            elif action == "DELETE":
                conn.execute("DELETE FROM users WHERE email=?", (target_email,))
                st.error("User Deleted.")
            conn.commit(); time.sleep(1); st.rerun()

    conn.close()

def user_dashboard():
    st.sidebar.title(f"👤 {st.session_state.user['name']}")
    if st.sidebar.button("LOGOUT"): st.session_state.user=None; st.rerun()
    
    st.title("🏭 Video Factory")
    
    # Charts
    st.markdown("### 📊 Your Analytics")
    chart_data = pd.DataFrame({"Day": range(7), "Views": [random.randint(100, 1000) for _ in range(7)]})
    st.plotly_chart(px.line(chart_data, x="Day", y="Views", template="plotly_dark"), use_container_width=True)
    
    st.write("---")
    
    # Factory
    c1, c2 = st.columns(2)
    f1 = c1.file_uploader("Hook Video")
    f2 = c2.file_uploader("Body Video")
    
    if st.button("🚀 LAUNCH PRODUCTION"):
        if f1 and f2:
            with st.status("Processing..."):
                path = process_video_logic([f1, f2])
                st.success("✅ Done!")
                st.video(path)
                st.info(ai_brain("Viral title"))
        else: st.error("Upload files")

def payment_page():
    st.title("⚠️ ACCOUNT LOCKED")
    st.info("Pay $10 to unlock.")
    st.write("JazzCash: 0320 1847179")
    
    tid = st.text_input("Transaction ID")
    if st.button("SUBMIT"):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO payments VALUES (?, ?, ?, ?, ?)", 
                  (st.session_state.user['email'], tid, "proof", "REVIEW", str(datetime.now())))
        conn.execute("UPDATE users SET status='REVIEW' WHERE email=?", (st.session_state.user['email'],))
        conn.commit(); conn.close()
        st.session_state.user['role'] = 'REVIEW'
        st.success("Sent!"); st.rerun()

# --- ROUTER ---
if 'user' not in st.session_state: st.session_state.user = None

if not st.session_state.user:
    login_page()
else:
    role = st.session_state.user['role']
    if role == 'ADMIN': admin_panel()
    elif role == 'ACTIVE': user_dashboard()
    elif role == 'REVIEW': 
        st.info("⏳ Admin is reviewing...")
        if st.button("Check Status"):
            conn = sqlite3.connect(DB_PATH)
            new_role = conn.execute("SELECT status FROM users WHERE email=?", (st.session_state.user['email'],)).fetchone()[0]
            conn.close()
            st.session_state.user['role'] = new_role
            st.rerun()
    else: payment_page()
    
        
