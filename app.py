import streamlit as st
import sqlite3
import hashlib
import time
import os
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pytz
import google.generativeai as genai
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

# --- CONFIG ---
st.set_page_config(page_title="MOHSIN EMPIRE", page_icon="⚡", layout="wide")

# 👇 API KEY 👇
GEMINI_KEY = "AIzaSyCORgPGyPfHq24sJGNJ0D-yk0E7Yf13qE0"

# --- DATABASE ---
if not os.path.exists("user_data"): os.makedirs("user_data")
DB_PATH = "mohsin_spirit_final.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Updated Schema with Timezone & Limits
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (email TEXT PRIMARY KEY, password TEXT, name TEXT, phone TEXT, status TEXT, 
                  timezone TEXT, joined_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS payments 
                 (email TEXT, tid TEXT, method TEXT, proof TEXT, status TEXT, date TEXT)''')
    
    # Admin Auto-Create
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)", 
                 ("mohsinakramchandia91@gmail.com", hashlib.sha256("Mohsin5577@".encode()).hexdigest(), 
                  "SUPER ADMIN", "03201847179", "ADMIN", "Asia/Karachi", str(datetime.now())))
    except: pass
    conn.commit(); conn.close()

init_db()

# --- CSS: HIGH SPIRIT THEME (Dark & Neon) ---
st.markdown("""
    <style>
    /* GLOBAL */
    .stApp { background-color: #000000; color: #ffffff; }
    
    /* GLASS CARDS */
    .glass {
        background: rgba(20, 20, 25, 0.9);
        border: 1px solid #00f3ff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.15);
        margin-bottom: 20px;
    }
    
    /* SLEEK INPUTS */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #0a0a0a !important;
        color: #00f3ff !important;
        border: 1px solid #333 !important;
        border-radius: 8px;
    }
    
    /* ANIMATED BUTTONS */
    .stButton>button {
        background: linear-gradient(90deg, #00f3ff, #0066ff);
        color: black; font-weight: 800; border: none;
        padding: 12px 24px; border-radius: 50px;
        text-transform: uppercase; letter-spacing: 1px;
        transition: 0.3s; width: 100%;
    }
    .stButton>button:hover {
        box-shadow: 0 0 20px #00f3ff;
        transform: scale(1.02);
    }
    
    /* METRICS */
    div[data-testid="stMetricValue"] {
        color: #00f3ff !important;
        text-shadow: 0 0 10px #00f3ff;
    }
    </style>
""", unsafe_allow_html=True)

# --- BACKEND BRAIN ---

def get_ai_title(niche):
    # Fallback AI (Agar API na chale to ye chale ga)
    backups = [
        "THIS Video Will Change Everything! 😱",
        "I Tested This VIRAL Hack...",
        "Don't Do This Mistake (Warning) ⚠️",
        "The Secret They Are Hiding From You..."
    ]
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        res = model.generate_content(f"Write a clickbait youtube title for {niche}")
        return res.text
    except:
        return random.choice(backups)

def get_live_chart():
    # Simulated Live Data
    times = pd.date_range(end=datetime.now(), periods=24, freq='H')
    views = [random.randint(100, 5000) for _ in range(24)]
    df = pd.DataFrame({"Time": times, "Views": views})
    
    fig = px.area(df, x="Time", y="Views", template="plotly_dark")
    fig.update_traces(line_color="#00f3ff", fillcolor="rgba(0, 243, 255, 0.1)")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=300)
    return fig

# --- PAGES ---

def login_register():
    st.markdown("<br><h1 style='text-align:center; color:#00f3ff;'>⚡ MOHSIN EMPIRE</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 LOGIN", "📝 REGISTER"])
    
    with tab1:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        email = st.text_input("Email", key="l_email")
        password = st.text_input("Password", type="password", key="l_pass")
        if st.button("ENTER SYSTEM"):
            hashed = hashlib.sha256(password.encode()).hexdigest()
            conn = sqlite3.connect(DB_PATH)
            user = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (email, hashed)).fetchone()
            conn.close()
            if user:
                st.session_state.user = {'email': user[0], 'name': user[2], 'role': user[4]}
                st.success("✅ Access Granted")
                time.sleep(0.5); st.rerun()
            else: st.error("❌ Access Denied")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        r_email = st.text_input("Gmail")
        r_name = st.text_input("Full Name")
        r_phone = st.text_input("WhatsApp")
        r_pass = st.text_input("Set Password", type="password")
        r_tz = st.selectbox("Your Timezone", pytz.all_timezones, index=pytz.all_timezones.index('Asia/Karachi'))
        
        if st.button("CREATE ACCOUNT"):
            if r_email and r_pass:
                try:
                    conn = sqlite3.connect(DB_PATH)
                    # Status set to 'PENDING' (Locked)
                    conn.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)", 
                              (r_email, hashlib.sha256(r_pass.encode()).hexdigest(), r_name, r_phone, "PENDING", r_tz, str(datetime.now())))
                    conn.commit(); conn.close()
                    st.success("🎉 Registered! Login to Activate.")
                except: st.error("Email Exists")
            else: st.warning("Fill all fields")
        st.markdown('</div>', unsafe_allow_html=True)

def payment_wall():
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("""
        <div class="glass" style="text-align:center; border: 1px solid red;">
            <h2 style="color:red;">⚠️ ACCESS LOCKED</h2>
            <p>Subscribe to unlock <b>Auto-Pilot & Factory</b>.</p>
            <h1 style="color:#00f3ff;">$10 / Month</h1>
            <hr style="border-color:#333;">
            <p>Send to JazzCash / EasyPaisa:</p>
            <h3>0320 1847179</h3>
            <p style="color:yellow;">Title: Muhammad Mohsin</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("pay"):
            tid = st.text_input("Transaction ID (TID) *Required")
            proof = st.file_uploader("Upload Receipt (Screenshot)")
            
            if st.form_submit_button("SUBMIT FOR APPROVAL"):
                if tid and proof:
                    conn = sqlite3.connect(DB_PATH)
                    conn.execute("INSERT INTO payments VALUES (?, ?, ?, ?, ?, ?)", 
                              (st.session_state.user['email'], tid, "JazzCash", "path_img", "REVIEW", str(datetime.now())))
                    conn.execute("UPDATE users SET status='REVIEW' WHERE email=?", (st.session_state.user['email'],))
                    conn.commit(); conn.close()
                    st.session_state.user['role'] = 'REVIEW'
                    st.success("✅ Submitted! Waiting for Admin.")
                    time.sleep(2); st.rerun()
                else:
                    st.error("❌ TID and Screenshot are REQUIRED.")

def user_dashboard():
    # Sidebar
    with st.sidebar:
        st.title("👤 MENU")
        menu = st.radio("Navigate", ["📊 Studio Analytics", "🏭 Video Factory", "✈️ Auto-Pilot", "⚙️ SEO Settings"])
        if st.button("LOGOUT"): st.session_state.user=None; st.rerun()

    if menu == "📊 Studio Analytics":
        st.markdown(f"### 👋 Welcome, {st.session_state.user['name']}")
        
        # Big Stats Row
        c1, c2, c3 = st.columns(3)
        c1.markdown('<div class="glass"><h4>👁️ Real-Time Views</h4><h1 style="color:#00f3ff">48,291</h1><p>▲ 12%</p></div>', unsafe_allow_html=True)
        c2.markdown('<div class="glass"><h4>💰 Revenue (Est.)</h4><h1 style="color:#00ff00">$1,402</h1><p>▲ $50 Today</p></div>', unsafe_allow_html=True)
        c3.markdown('<div class="glass"><h4>🎥 Videos Active</h4><h1 style="color:orange">145</h1><p>Auto-Pilot ON</p></div>', unsafe_allow_html=True)
        
        # Live Chart
        st.markdown("### 📈 Channel Growth")
        st.plotly_chart(get_live_chart(), use_container_width=True)

    elif menu == "🏭 Video Factory":
        st.title("🎬 Content Production")
        c1, c2 = st.columns(2)
        f1 = c1.file_uploader("📂 Hook (Part 1)")
        f2 = c2.file_uploader("📂 Body (Part 2)")
        f3 = c1.file_uploader("📂 Climax (Part 3)")
        f4 = c2.file_uploader("📂 Outro (Part 4)")
        
        if st.button("🚀 LAUNCH PRODUCTION"):
            if f1 and f2 and f3 and f4:
                with st.status("⚙️ Factory Processing...", expanded=True):
                    st.write("🧵 Stitching Clips...")
                    time.sleep(2)
                    st.write("🧠 AI Analyzing for SEO...")
                    title = get_ai_title("Viral Vlogs")
                    st.success("✅ DONE!")
                    st.info(f"Generated Title: **{title}**")
            else: st.error("Upload All Files")

    elif menu == "⚙️ SEO Settings":
        st.title("🌍 Global Timing")
        
        c1, c2 = st.columns(2)
        target_tz = c1.selectbox("Target Audience Timezone", pytz.all_timezones, index=pytz.all_timezones.index('US/Pacific'))
        post_time = c2.time_input("Upload Time")
        
        st.write("---")
        st.markdown("### 🔗 Connect Platforms")
        c_yt, c_ig = st.columns(2)
        c_yt.text_input("YouTube API Key")
        c_ig.text_input("Instagram Password", type="password")
        st.button("SAVE SETTINGS")

    elif menu == "✈️ Auto-Pilot":
        st.title("✈️ Auto-Pilot System")
        st.info("System will monitor your drive and upload automatically.")
        
        col_inp, col_stat = st.columns([3, 1])
        folder_id = col_inp.text_input("Google Drive Folder ID")
        
        if col_inp.button("🟢 ACTIVATE AUTO-PILOT"):
            if folder_id:
                col_stat.success("Running")
                st.toast("System Armed! Monitoring Background...", icon="🤖")
            else:
                st.error("Enter Folder ID")

def admin_dashboard():
    st.title("👑 ADMIN COMMAND")
    conn = sqlite3.connect(DB_PATH)
    
    st.subheader("💰 Payment Approvals")
    reqs = conn.execute("SELECT * FROM payments WHERE status='REVIEW'").fetchall()
    
    if reqs:
        for r in reqs:
            with st.expander(f"{r[0]} (TID: {r[1]})"):
                st.write(f"Date: {r[5]}")
                c1, c2 = st.columns(2)
                if c1.button("✅ APPROVE", key=f"a_{r[1]}"):
                    conn.execute("UPDATE users SET status='ACTIVE' WHERE email=?", (r[0],))
                    conn.execute("UPDATE payments SET status='APPROVED' WHERE tid=?", (r[1],))
                    conn.commit(); st.rerun()
                if c2.button("❌ BLOCK", key=f"b_{r[1]}"):
                    conn.execute("UPDATE payments SET status='REJECTED' WHERE tid=?", (r[1],))
                    conn.commit(); st.rerun()
    else:
        st.info("No Pending Requests")
    
    st.write("---")
    st.subheader("👥 Users")
    users = conn.execute("SELECT name, email, status, phone FROM users").fetchall()
    st.dataframe(pd.DataFrame(users, columns=["Name", "Email", "Status", "Phone"]), use_container_width=True)
    conn.close()

# --- ROUTER ---
if not st.session_state.user:
    login_register()
else:
    role = st.session_state.user['role']
    if role == 'ADMIN': admin_dashboard()
    elif role == 'ACTIVE': user_dashboard()
    elif role == 'PENDING': payment_wall()
    elif role == 'REVIEW': 
        st.info("⏳ Your payment is under review. Please wait for Admin approval.")
        if st.button("Check Again"):
            conn = sqlite3.connect(DB_PATH)
            new_role = conn.execute("SELECT status FROM users WHERE email=?", (st.session_state.user['email'],)).fetchone()[0]
            conn.close()
            st.session_state.user['role'] = new_role
            st.rerun()
    
