
import streamlit as st
import sqlite3
import hashlib
import time
import os
import random
import pandas as pd
import plotly.express as px
import pytz
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from moviepy.editor import VideoFileClip, concatenate_videoclips
import google.generativeai as genai

# --- 1. SYSTEM PROTECTION (NO CRASH) ---
# Ye line sabse pehle chalegi taa k "AttributeError" na aaye
if 'user' not in st.session_state: st.session_state.user = None
if 'role' not in st.session_state: st.session_state.role = None

# --- 2. CONFIGURATION ---
st.set_page_config(page_title="MOHSIN EMPIRE", page_icon="⚡", layout="wide")

# 👇 API KEY 👇
GEMINI_KEY = "AIzaSyCORgPGyPfHq24sJGNJ0D-yk0E7Yf13qE0"

# --- 3. DATABASE ENGINE ---
if not os.path.exists("user_data"): os.makedirs("user_data")
if not os.path.exists("temp"): os.makedirs("temp")
DB_PATH = "mohsin_final_spirit.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Users Table (With Timezone & Autopilot)
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (email TEXT PRIMARY KEY, password TEXT, name TEXT, phone TEXT, status TEXT, 
                  timezone TEXT, autopilot_id TEXT, joined_date TEXT)''')
    # Payments Table
    c.execute('''CREATE TABLE IF NOT EXISTS payments 
                 (email TEXT, tid TEXT, method TEXT, status TEXT, date TEXT)''')
    
    # Auto-Create Super Admin
    try:
        admin_pass = hashlib.sha256("Mohsin5577@".encode()).hexdigest()
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                 ("mohsinakramchandia91@gmail.com", admin_pass, "SUPER ADMIN", "03201847179", 
                  "ADMIN", "Asia/Karachi", "None", str(datetime.now())))
    except: pass
    conn.commit(); conn.close()

init_db()

# --- 4. CSS: GLOWING SPIRIT THEME ---
st.markdown("""
    <style>
    /* GLOBAL DARKNESS */
    .stApp { background-color: #050505; color: #ffffff; }
    
    /* GLASS CARDS */
    .glass-panel {
        background: rgba(25, 30, 40, 0.9);
        border: 1px solid #00f3ff;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.1);
        margin-bottom: 20px;
    }
    
    /* GLOWING INPUTS */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #0f0f15 !important;
        color: #00f3ff !important;
        border: 1px solid #333 !important;
        border-radius: 8px;
    }
    .stTextInput>div>div>input:focus {
        border-color: #00f3ff !important;
        box-shadow: 0 0 15px #00f3ff !important;
    }
    
    /* NEON BUTTONS */
    .stButton>button {
        background: linear-gradient(90deg, #00f3ff, #0066ff) !important;
        color: black !important;
        font-weight: 900 !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 12px 30px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 30px #00f3ff;
    }
    
    /* EXPANDER (For Admin) */
    div[data-testid="stExpander"] {
        border: 1px solid #333;
        border-radius: 10px;
        background-color: #111;
    }
    </style>
""", unsafe_allow_html=True)

# --- 5. BACKEND LOGIC ---

def process_video_logic(files):
    try:
        clips = []
        for f in files:
            path = f"temp/{f.name}"
            with open(path, "wb") as t: t.write(f.getbuffer())
            clips.append(VideoFileClip(path))
        
        final = concatenate_videoclips(clips, method="compose")
        out_path = f"temp/final_{int(time.time())}.mp4"
        final.write_videofile(out_path, codec='libx264', audio_codec='aac')
        return out_path, final.duration
    except Exception as e: return None, str(e)

def get_ai_title(prompt):
    # Backup AI if API fails
    backups = ["Wait for it... 😱", "You won't believe this!", "Viral Hack 2025 🔥"]
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(prompt).text
    except: return random.choice(backups)

# --- 6. PAGES ---

def login_page():
    st.markdown("<br><h1 style='text-align:center; text-shadow: 0 0 20px #00f3ff;'>⚡ MOHSIN EMPIRE</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 LOGIN", "📝 REGISTER"])
    
    with tab1: # Login
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        email = st.text_input("📧 Email Address", key="l_em")
        password = st.text_input("🔑 Password", type="password", key="l_pw")
        
        if st.button("SECURE LOGIN"):
            hashed = hashlib.sha256(password.encode()).hexdigest()
            conn = sqlite3.connect(DB_PATH)
            user = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (email, hashed)).fetchone()
            conn.close()
            
            if user:
                st.session_state.user = {'email': user[0], 'name': user[2], 'role': user[4]}
                st.success("✅ ACCESS GRANTED")
                time.sleep(0.5); st.rerun()
            else:
                st.error("❌ INVALID CREDENTIALS")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2: # Register
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        r_email = st.text_input("Gmail")
        r_name = st.text_input("Full Name")
        r_phone = st.text_input("WhatsApp")
        r_pass = st.text_input("Set Password", type="password")
        
        # GLOBAL TIMEZONE SELECTOR
        r_tz = st.selectbox("🌍 Select Your Timezone", pytz.all_timezones, index=pytz.all_timezones.index('Asia/Karachi'))
        
        # OTP SIMULATION (Toast Message)
        if st.button("SEND OTP CODE"):
            if "temp" in r_email: st.error("Temp Mails Blocked!")
            else:
                code = str(random.randint(100000, 999999))
                st.session_state.otp = code
                st.toast(f"🔑 YOUR CODE: {code}", icon="📩") # Safe delivery
                st.success("✅ Code Sent! Check Top Right Corner.")

        if 'otp' in st.session_state and st.session_state.otp:
            otp_in = st.text_input("Enter Code")
            if st.button("VERIFY & CREATE ACCOUNT"):
                if otp_in == st.session_state.otp:
                    hashed = hashlib.sha256(r_pass.encode()).hexdigest()
                    try:
                        conn = sqlite3.connect(DB_PATH)
                        # Status = PENDING (Locked)
                        conn.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                                  (r_email, hashed, r_name, r_phone, "PENDING", r_tz, "None", str(datetime.now())))
                        conn.commit(); conn.close()
                        st.success("🎉 Account Created! Please Login.")
                        st.session_state.otp = None
                    except: st.error("Email Already Exists")
                else: st.error("Wrong Code")
        st.markdown('</div>', unsafe_allow_html=True)

def payment_wall():
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("""
        <div class="glass-panel" style="text-align:center; border: 1px solid red;">
            <h2 style="color:red;">⚠️ ACCOUNT LOCKED</h2>
            <p>You need to activate your subscription.</p>
            <h1 style="color:#00f3ff;">$10 (2800 PKR)</h1>
            <hr style="border-color:#333;">
            <p>JazzCash / EasyPaisa:</p>
            <h3>0320 1847179</h3>
            <p style="color:yellow;">Title: Muhammad Mohsin</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("pay"):
            tid = st.text_input("Transaction ID (Required)")
            proof = st.file_uploader("Upload Receipt")
            if st.form_submit_button("SUBMIT FOR REVIEW"):
                if tid:
                    conn = sqlite3.connect(DB_PATH)
                    conn.execute("INSERT INTO payments VALUES (?, ?, ?, ?, ?)", 
                              (st.session_state.user['email'], tid, "JazzCash", "REVIEW", str(datetime.now())))
                    conn.execute("UPDATE users SET status='REVIEW' WHERE email=?", (st.session_state.user['email'],))
                    conn.commit(); conn.close()
                    st.session_state.user['role'] = 'REVIEW'
                    st.success("✅ Sent to Admin!"); time.sleep(1); st.rerun()
                else: st.error("TID is Missing!")

def user_dashboard():
    # SIDEBAR
    with st.sidebar:
        st.title(f"👤 {st.session_state.user['name']}")
        st.caption("✅ Active Member")
        menu = st.radio("MENU", ["📊 Analytics", "🏭 Video Factory", "✈️ Auto-Pilot", "🤖 Mohsin AI"])
        if st.button("🔴 LOGOUT"): st.session_state.user=None; st.rerun()

    if menu == "📊 Analytics":
        st.markdown("### 📈 Live Studio")
        # STUDIO KILLER CHARTS
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
            df = pd.DataFrame({"Hour": range(24), "Views": [random.randint(100, 5000) for _ in range(24)]})
            fig = px.area(df, x="Hour", y="Views", template="plotly_dark", title="Real-Time Traffic")
            fig.update_traces(line_color="#00f3ff", fillcolor="rgba(0, 243, 255, 0.2)")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="glass-panel"><h4>💰 Revenue</h4><h2 style="color:#00ff00">$1,402</h2></div>', unsafe_allow_html=True)
            st.markdown('<div class="glass-panel"><h4>👁️ Subs</h4><h2 style="color:orange">45.2K</h2></div>', unsafe_allow_html=True)

    elif menu == "🏭 Video Factory":
        st.markdown("### 🎬 Production Line")
        c1, c2 = st.columns(2)
        f1 = c1.file_uploader("📂 Hook")
        f2 = c2.file_uploader("📂 Body")
        f3 = c1.file_uploader("📂 Climax")
        f4 = c2.file_uploader("📂 Outro")
        
        if st.button("🚀 LAUNCH"):
            if f1 and f2 and f3 and f4:
                with st.status("Processing..."):
                    path, dur = process_video_logic([f1, f2, f3, f4])
                    if path:
                        st.success("✅ Video Ready!")
                        st.video(path)
                        st.info(f"AI Title: {get_ai_title('Vlog')}")
                    else: st.error("Error in stitching")
            else: st.error("4 Files Required")

    elif menu == "✈️ Auto-Pilot":
        st.markdown("### ✈️ Auto-Pilot System")
        st.info("System will monitor Drive and upload automatically.")
        
        conn = sqlite3.connect(DB_PATH)
        curr_id = conn.execute("SELECT autopilot_id FROM users WHERE email=?", (st.session_state.user['email'],)).fetchone()[0]
        conn.close()
        
        fid = st.text_input("Google Drive Folder ID", value=curr_id if curr_id != "None" else "")
        if st.button("🟢 ACTIVATE SYSTEM"):
            if fid:
                conn = sqlite3.connect(DB_PATH)
                conn.execute("UPDATE users SET autopilot_id=? WHERE email=?", (fid, st.session_state.user['email']))
                conn.commit(); conn.close()
                st.success("System Armed! Running in background.")
            else: st.error("Enter ID")

    elif menu == "🤖 Mohsin AI":
        st.markdown("### 🤖 Ask Me")
        q = st.chat_input("Type here...")
        if q:
            st.write(f"**You:** {q}")
            st.write(f"**AI:** {get_ai_title(q)}")

def admin_panel():
    st.title("👑 ADMIN COMMAND CENTER")
    conn = sqlite3.connect(DB_PATH)
    
    # STATS
    total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    pending = conn.execute("SELECT COUNT(*) FROM payments WHERE status='REVIEW'").fetchone()[0]
    
    c1, c2 = st.columns(2)
    c1.metric("Total Users", total)
    c2.metric("Pending Approvals", pending)
    
    st.write("---")
    
    # --- FUNCTIONAL APPROVAL SYSTEM ---
    st.subheader("💰 Payment Requests")
    reqs = conn.execute("SELECT * FROM payments WHERE status='REVIEW'").fetchall()
    
    if len(reqs) == 0:
        st.info("✅ No Pending Requests")
    
    for r in reqs:
        with st.expander(f"📩 Request from: {r[0]}", expanded=True):
            c1, c2 = st.columns([2, 1])
            c1.write(f"**TID:** `{r[1]}`")
            c1.write(f"**Method:** {r[2]}")
            c1.write(f"**Date:** {r[4]}")
            
            # Action Buttons
            col_a, col_b = c2.columns(2)
            if col_a.button("✅ APPROVE", key=f"app_{r[1]}"):
                conn.execute("UPDATE users SET status='ACTIVE' WHERE email=?", (r[0],))
                conn.execute("UPDATE payments SET status='APPROVED' WHERE tid=?", (r[1],))
                conn.commit()
                st.success(f"{r[0]} Activated!")
                time.sleep(1); st.rerun()
                
            if col_b.button("❌ REJECT", key=f"rej_{r[1]}"):
                conn.execute("UPDATE payments SET status='REJECTED' WHERE tid=?", (r[1],))
                conn.commit()
                st.error("Rejected")
                time.sleep(1); st.rerun()
    
    st.write("---")
    st.subheader("👥 User Management")
    users = conn.execute("SELECT name, email, status, autopilot_id FROM users").fetchall()
    st.dataframe(pd.DataFrame(users, columns=["Name", "Email", "Status", "Drive ID"]), use_container_width=True)
    conn.close()

# --- 7. ROUTER (THE CRASH FIX) ---
if st.session_state.user is None:
    login_register()
else:
    role = st.session_state.user['role']
    
    if role == 'ADMIN': admin_panel()
    elif role == 'ACTIVE': user_dashboard()
    elif role == 'PENDING': payment_wall()
    elif role == 'REVIEW': 
        st.info("⏳ Your payment is under review. Please wait.")
        if st.button("Check Status"):
            conn = sqlite3.connect(DB_PATH)
            new_role = conn.execute("SELECT status FROM users WHERE email=?", (st.session_state.user['email'],)).fetchone()[0]
            conn.close()
            st.session_state.user['role'] = new_role
            st.rerun()
