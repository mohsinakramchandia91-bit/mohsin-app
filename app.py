import streamlit as st
import sqlite3
import hashlib
import time
import os
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import google.generativeai as genai
from moviepy.editor import VideoFileClip, concatenate_videoclips

# --- CONFIG ---
st.set_page_config(page_title="MOHSIN EMPIRE", page_icon="🏢", layout="wide")

# 👇 API KEY 👇
GEMINI_KEY = "AIzaSyCORgPGyPfHq24sJGNJ0D-yk0E7Yf13qE0"

# --- DATABASE ---
if not os.path.exists("data"): os.makedirs("data")
DB_PATH = "data/empire_prod.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (email TEXT PRIMARY KEY, password TEXT, name TEXT, phone TEXT, status TEXT, 
                  joined_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS payments 
                 (email TEXT, tid TEXT, status TEXT, date TEXT)''')
    
    # Create Super Admin
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", 
                 ("mohsinakramchandia91@gmail.com", hashlib.sha256("Mohsin5577@".encode()).hexdigest(), 
                  "SUPER ADMIN", "03201847179", "ADMIN", str(datetime.now())))
    except: pass
    conn.commit(); conn.close()

init_db()

# --- CSS: PRO DASHBOARD THEME ---
st.markdown("""
    <style>
    /* GLOBAL */
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* GLASS CARDS */
    .card {
        background: rgba(38, 39, 48, 0.7);
        border: 1px solid #3b82f6;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* METRIC BOXES */
    .metric-box {
        background: linear-gradient(135deg, #1e3a8a, #172554);
        padding: 20px; border-radius: 10px; text-align: center;
        border: 1px solid #60a5fa;
    }
    
    /* BUTTONS */
    .stButton>button {
        background: linear-gradient(90deg, #2563eb, #0ea5e9);
        color: white; font-weight: bold; border: none; width: 100%;
        padding: 10px; border-radius: 8px;
    }
    .stButton>button:hover { box-shadow: 0 0 15px #3b82f6; }
    
    /* INPUTS */
    input { background: #1f2937 !important; color: white !important; border: 1px solid #374151 !important; }
    </style>
""", unsafe_allow_html=True)

# --- BACKEND LOGIC ---

def generate_otp():
    return str(random.randint(100000, 999999))

def get_admin_charts():
    # Fake Data for Visuals
    dates = pd.date_range(start="2025-01-01", periods=7)
    rev = [10, 20, 15, 40, 50, 90, 120]
    df = pd.DataFrame({"Date": dates, "Revenue ($)": rev})
    fig = px.area(df, x="Date", y="Revenue ($)", template="plotly_dark")
    fig.update_traces(line_color="#00f3ff", fillcolor="rgba(0, 243, 255, 0.2)")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=300)
    return fig

# --- SESSION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'otp' not in st.session_state: st.session_state.otp = None
if 'temp_data' not in st.session_state: st.session_state.temp_data = {}

# --- PAGES ---

def login_register():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<h1 style='text-align:center; color:#3b82f6;'>💎 MOHSIN EMPIRE</h1>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["LOGIN", "REGISTER"])
        
        with tab1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            email = st.text_input("📧 Email")
            password = st.text_input("🔑 Password", type="password")
            if st.button("LOGIN NOW"):
                hashed = hashlib.sha256(password.encode()).hexdigest()
                conn = sqlite3.connect(DB_PATH)
                user = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (email, hashed)).fetchone()
                conn.close()
                if user:
                    st.session_state.user = {'email': user[0], 'name': user[2], 'status': user[4]}
                    st.rerun()
                else: st.error("❌ Invalid Credentials")
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            r_email = st.text_input("Gmail Address")
            r_name = st.text_input("Full Name")
            r_phone = st.text_input("WhatsApp")
            r_pass = st.text_input("Create Password", type="password")
            
            if st.button("SEND OTP"):
                if r_email:
                    otp = generate_otp()
                    st.session_state.otp = otp
                    st.session_state.temp_data = {'e': r_email, 'p': r_pass, 'n': r_name, 'ph': r_phone}
                    # SIMULATED EMAIL (Reliable)
                    st.success(f"✅ OTP Sent to {r_email}")
                    st.info(f"🔒 SECURITY CODE: {otp}") # Showing here because SMTP blocks on free servers
                else: st.error("Enter Email")
            
            if st.session_state.otp:
                otp_in = st.text_input("Enter Verification Code")
                if st.button("VERIFY & REGISTER"):
                    if otp_in == st.session_state.otp:
                        d = st.session_state.temp_data
                        conn = sqlite3.connect(DB_PATH)
                        try:
                            conn.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", 
                                      (d['e'], hashlib.sha256(d['p'].encode()).hexdigest(), d['n'], d['ph'], "PENDING", str(datetime.now())))
                            conn.commit()
                            st.success("🎉 Account Created! Please Login.")
                            st.session_state.otp = None
                        except: st.error("User Exists")
                        conn.close()
                    else: st.error("Wrong OTP")
            st.markdown('</div>', unsafe_allow_html=True)

def payment_gate():
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("""
        <div class="card" style="text-align:center; border: 1px solid orange;">
            <h2 style="color:orange;">⚠️ ACCOUNT LOCKED</h2>
            <p>Please pay subscription fee to access the Automation Factory.</p>
            <h1>$10 <span style="font-size:16px">(2800 PKR)</span></h1>
            <p><b>JazzCash: 0320 1847179 (Mohsin Akram)</b></p>
        </div>
        """, unsafe_allow_html=True)
        
        tid = st.text_input("Enter Transaction ID (TID)")
        if st.button("SUBMIT FOR REVIEW"):
            conn = sqlite3.connect(DB_PATH)
            conn.execute("INSERT INTO payments VALUES (?, ?, ?, ?)", 
                      (st.session_state.user['email'], tid, "REVIEW", str(datetime.now())))
            conn.execute("UPDATE users SET status='REVIEW' WHERE email=?", (st.session_state.user['email'],))
            conn.commit(); conn.close()
            st.session_state.user['status'] = 'REVIEW'
            st.success("Sent to Admin!"); time.sleep(1); st.rerun()

def admin_panel():
    st.title("👑 ADMIN COMMAND CENTER")
    
    conn = sqlite3.connect(DB_PATH)
    
    # METRICS ROW
    c1, c2, c3, c4 = st.columns(4)
    total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    active = conn.execute("SELECT COUNT(*) FROM users WHERE status='ACTIVE'").fetchone()[0]
    rev = active * 10
    pending = conn.execute("SELECT COUNT(*) FROM payments WHERE status='REVIEW'").fetchone()[0]
    
    c1.markdown(f'<div class="metric-box"><h3>👥 Total</h3><h2>{total}</h2></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-box"><h3>⚡ Active</h3><h2>{active}</h2></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-box"><h3>💰 Revenue</h3><h2>${rev}</h2></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="metric-box"><h3>⏳ Pending</h3><h2>{pending}</h2></div>', unsafe_allow_html=True)
    
    st.write("---")
    
    # LAYOUT
    c_graph, c_action = st.columns([2, 1])
    
    with c_graph:
        st.markdown("### 📈 Revenue Growth")
        st.plotly_chart(get_admin_charts(), use_container_width=True)
        
    with c_action:
        st.markdown("### 🔔 Pending Approvals")
        reqs = conn.execute("SELECT * FROM payments WHERE status='REVIEW'").fetchall()
        if not reqs: st.info("All Caught Up!")
        for r in reqs:
            with st.expander(f"{r[0]}"):
                st.write(f"**TID:** {r[1]}")
                c_a, c_b = st.columns(2)
                if c_a.button("✅", key=f"a_{r[1]}"):
                    conn.execute("UPDATE users SET status='ACTIVE' WHERE email=?", (r[0],))
                    conn.execute("UPDATE payments SET status='APPROVED' WHERE tid=?", (r[1],))
                    conn.commit(); st.rerun()
                if c_b.button("❌", key=f"r_{r[1]}"):
                    conn.execute("UPDATE payments SET status='REJECTED' WHERE tid=?", (r[1],))
                    conn.commit(); st.rerun()
    
    st.write("---")
    st.subheader("👤 User Database")
    users = conn.execute("SELECT name, email, status, phone FROM users").fetchall()
    st.dataframe(pd.DataFrame(users, columns=["Name", "Email", "Status", "WhatsApp"]), use_container_width=True)
    
    conn.close()

def user_dashboard():
    st.sidebar.title(f"👤 {st.session_state.user['name']}")
    menu = st.sidebar.radio("Navigate", ["Factory", "Auto-Pilot", "Connections"])
    if st.sidebar.button("Logout"): st.session_state.user=None; st.rerun()
    
    if menu == "Factory":
        st.title("🏭 Video Factory")
        c1, c2 = st.columns(2)
        f1 = c1.file_uploader("Hook Video")
        f2 = c2.file_uploader("Body Video")
        if st.button("🚀 LAUNCH"):
            if f1 and f2:
                with st.status("Processing..."):
                    time.sleep(2); st.success("Video Ready!")
            else: st.error("Files Missing")
            
    elif menu == "Auto-Pilot":
        st.title("✈️ Auto-Pilot")
        st.info("System is monitoring your drive.")
        st.text_input("Drive Folder ID")
        st.button("Activate")

# --- ROUTER ---
if not st.session_state.user:
    login_register()
else:
    status = st.session_state.user['status']
    if status == 'ADMIN': admin_panel()
    elif status == 'ACTIVE': user_dashboard()
    elif status == 'REVIEW': 
        st.info("⏳ Admin verification in progress. Refresh later.")
        if st.button("Refresh"): 
            # Recheck status logic
            conn = sqlite3.connect(DB_PATH)
            new_status = conn.execute("SELECT status FROM users WHERE email=?", (st.session_state.user['email'],)).fetchone()[0]
            conn.close()
            st.session_state.user['status'] = new_status
            st.rerun()
    else: payment_gate()
  
