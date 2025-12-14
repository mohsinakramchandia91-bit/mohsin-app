
import streamlit as st
import sqlite3
import hashlib
import time
import os
import random
import pandas as pd
import plotly.express as px
import pytz
import google.generativeai as genai
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

# --- 1. CONFIGURATION (MUST BE FIRST) ---
st.set_page_config(page_title="MOHSIN EMPIRE", page_icon="💎", layout="wide")

# --- 2. CRASH PROTECTION (SESSION STATE FIX) ---
# Ye code sabse pehle chalega taa k "AttributeError" na aaye
if 'user' not in st.session_state:
    st.session_state.user = None
if 'role' not in st.session_state:
    st.session_state.role = None

# --- 3. DATABASE SETUP ---
if not os.path.exists("user_data"): os.makedirs("user_data")
DB_PATH = "mohsin_diamond_final.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (email TEXT PRIMARY KEY, password TEXT, name TEXT, phone TEXT, status TEXT, 
                  timezone TEXT, joined_date TEXT)''')
    # Payments Table
    c.execute('''CREATE TABLE IF NOT EXISTS payments 
                 (email TEXT, tid TEXT, proof TEXT, status TEXT, date TEXT)''')
    
    # Auto-Create Admin (Mohsin)
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)", 
                 ("mohsinakramchandia91@gmail.com", hashlib.sha256("Mohsin5577@".encode()).hexdigest(), 
                  "SUPER ADMIN", "03201847179", "ADMIN", "Asia/Karachi", str(datetime.now())))
    except: pass
    conn.commit(); conn.close()

init_db()

# --- 4. CSS: DIAMOND THEME ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    
    /* GLASS CARDS */
    .glass {
        background: rgba(20, 25, 30, 0.9);
        border: 1px solid #00f3ff;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.15);
        margin-bottom: 20px;
    }
    
    /* INPUTS */
    input, select { 
        background-color: #0a0a0a !important; 
        color: #00f3ff !important; 
        border: 1px solid #333 !important; 
        border-radius: 8px !important;
    }
    
    /* BUTTONS */
    button {
        background: linear-gradient(90deg, #00f3ff, #0066ff) !important;
        color: black !important; font-weight: 800 !important;
        border: none !important; border-radius: 50px !important;
        padding: 10px 20px !important; width: 100%;
    }
    button:hover { box-shadow: 0 0 25px #00f3ff; transform: scale(1.02); }
    </style>
""", unsafe_allow_html=True)

# --- 5. BACKEND LOGIC ---

# API Key
GEMINI_KEY = "AIzaSyCORgPGyPfHq24sJGNJ0D-yk0E7Yf13qE0"

def get_ai_title(niche):
    # Backup Brain (Agar Google API fail ho to ye chalega)
    backups = [
        "Use This Secret Hack! 😱",
        "I Exposed The Truth...",
        "Don't Miss This Warning ⚠️",
        "100% Viral Strategy Revealed"
    ]
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        res = model.generate_content(f"Write a clickbait youtube title for {niche}")
        return res.text
    except:
        return random.choice(backups)

def get_live_chart():
    # Studio-Like Analytics
    df = pd.DataFrame({
        "Hour": [f"{i}:00" for i in range(24)],
        "Views": [random.randint(100, 5000) for _ in range(24)]
    })
    fig = px.area(df, x="Hour", y="Views", template="plotly_dark")
    fig.update_traces(line_color="#00f3ff", fillcolor="rgba(0, 243, 255, 0.2)")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=300)
    return fig

# --- 6. PAGES ---

def login_register():
    st.markdown("<br><h1 style='text-align:center; color:#00f3ff;'>⚡ MOHSIN EMPIRE</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 LOGIN", "📝 REGISTER"])
    
    with tab1: # Login
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
            else:
                st.error("❌ Access Denied")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2: # Register
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        r_email = st.text_input("Gmail")
        r_name = st.text_input("Full Name")
        r_phone = st.text_input("WhatsApp")
        r_pass = st.text_input("Set Password", type="password")
        r_tz = st.selectbox("Timezone", pytz.all_timezones, index=pytz.all_timezones.index('Asia/Karachi'))
        
        if st.button("CREATE ACCOUNT"):
            if r_email and r_pass:
                try:
                    conn = sqlite3.connect(DB_PATH)
                    # Status = PENDING (User locked until payment)
                    conn.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)", 
                              (r_email, hashlib.sha256(r_pass.encode()).hexdigest(), r_name, r_phone, "PENDING", r_tz, str(datetime.now())))
                    conn.commit(); conn.close()
                    st.success("🎉 Account Created! Please Login to Activate.")
                except: st.error("Email Already Registered")
            else: st.warning("Fill All Fields")
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
            tid = st.text_input("Transaction ID (TID)")
            if st.form_submit_button("SUBMIT PROOF"):
                if tid:
                    conn = sqlite3.connect(DB_PATH)
                    conn.execute("INSERT INTO payments VALUES (?, ?, ?, ?, ?)", 
                              (st.session_state.user['email'], tid, "No Image", "REVIEW", str(datetime.now())))
                    conn.execute("UPDATE users SET status='REVIEW' WHERE email=?", (st.session_state.user['email'],))
                    conn.commit(); conn.close()
                    
                    st.session_state.user['role'] = 'REVIEW'
                    st.success("✅ Submitted! Waiting for Admin."); time.sleep(2); st.rerun()
                else: st.error("TID Required")

def user_dashboard():
    # Sidebar
    with st.sidebar:
        st.title("👤 MENU")
        menu = st.radio("Navigate", ["📊 Analytics", "🏭 Factory", "✈️ Auto-Pilot", "⚙️ Settings"])
        if st.button("LOGOUT"): st.session_state.user=None; st.rerun()

    if menu == "📊 Analytics":
        st.markdown(f"### 👋 Welcome, {st.session_state.user['name']}")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="glass"><h4>👁️ Real-Time Views</h4><h1 style="color:#00f3ff">1.2M</h1></div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="glass"><h4>💰 Revenue</h4><h1 style="color:#00ff00">$2,400</h1></div>', unsafe_allow_html=True)
        st.markdown("### 📈 Channel Growth")
        st.plotly_chart(get_live_chart(), use_container_width=True)

    elif menu == "🏭 Factory":
        st.title("🎬 Video Factory")
        c1, c2 = st.columns(2)
        f1 = c1.file_uploader("📂 Hook")
        f2 = c2.file_uploader("📂 Body")
        if st.button("🚀 LAUNCH"):
            if f1 and f2:
                with st.status("Processing..."):
                    time.sleep(2)
                    title = get_ai_title("Vlog")
                    st.success("✅ Done!")
                    st.info(f"AI Title: {title}")
            else: st.error("Upload files")

    elif menu == "✈️ Auto-Pilot":
        st.title("✈️ Auto-Pilot")
        st.info("System Monitors Drive 24/7.")
        fid = st.text_input("Drive Folder ID")
        if st.button("ACTIVATE"):
            st.success("Armed!")

    elif menu == "⚙️ Settings":
        st.title("🌍 Settings")
        st.selectbox("Timezone", pytz.all_timezones)
        st.text_input("YouTube API Key")
        st.button("Save")

def admin_dashboard():
    st.title("👑 ADMIN PANEL")
    conn = sqlite3.connect(DB_PATH)
    
    st.subheader("💰 Payment Requests")
    reqs = conn.execute("SELECT * FROM payments WHERE status='REVIEW'").fetchall()
    
    if reqs:
        for r in reqs:
            with st.expander(f"{r[0]} (TID: {r[1]})"):
                if st.button("✅ Approve", key=f"a_{r[1]}"):
                    conn.execute("UPDATE users SET status='ACTIVE' WHERE email=?", (r[0],))
                    conn.execute("UPDATE payments SET status='APPROVED' WHERE tid=?", (r[1],))
                    conn.commit(); st.rerun()
    else: st.info("No Pending Requests")
    
    st.subheader("👥 Users")
    users = conn.execute("SELECT name, email, status FROM users").fetchall()
    st.dataframe(pd.DataFrame(users, columns=["Name", "Email", "Status"]), use_container_width=True)
    conn.close()

# --- 7. ROUTER (THE FIX IS HERE) ---
if st.session_state.user is None:
    login_register()
else:
    role = st.session_state.user['role']
    
    if role == 'ADMIN': admin_dashboard()
    elif role == 'ACTIVE': user_dashboard()
    elif role == 'PENDING': payment_wall()
    elif role == 'REVIEW': 
        st.info("⏳ Your payment is under review.")
        if st.button("Refresh Status"):
            conn = sqlite3.connect(DB_PATH)
            new_role = conn.execute("SELECT status FROM users WHERE email=?", (st.session_state.user['email'],)).fetchone()[0]
            conn.close()
            st.session_state.user['role'] = new_role
            st.rerun()
        
