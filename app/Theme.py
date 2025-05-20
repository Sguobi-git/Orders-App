import streamlit as st
import time
import requests
from streamlit_lottie import st_lottie

# ---------- Page Config ----------
st.set_page_config(
    page_title="Light Mode Tip",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------- CSS ----------
st.markdown("""
    <style>
    .big-title {
        font-size: 2.2em;
        font-weight: bold;
        color: #262730;
        text-align: center;
        margin-bottom: 1em;
    }
    .instruction-box {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.05);
        font-size: 1.1em;
        color: #333;
    }
    ul {
        padding-left: 1.2em;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- Lottie Animation Function ----------
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# ---------- Title ----------
st.markdown('<div class="big-title">Optimize Your Viewing Experience 🌞</div>', unsafe_allow_html=True)

# ---------- Animation ----------
lottie_url = "https://assets3.lottiefiles.com/packages/lf20_mcfvqjgx.json"
lottie_animation = load_lottieurl(lottie_url)
if lottie_animation:
    st_lottie(lottie_animation, height=250)

# ---------- Instructions ----------
st.markdown("""
<div class="instruction-box">
If this page appears dark, it means your browser or system is in dark mode.<br><br>
To switch to Light Mode:
<ul>
    <li>Click the <span style="font-size: 2em; margin-right: 10px; margin-left: 10px;">⋮</span> icon at the top-right corner</li>
    <li>Select <b>Settings</b></li>
    <li>Then choose <b>Appearance → Light</b></li>
</ul>
</div>
""", unsafe_allow_html=True)

# ---------- Button to continue ----------
st.markdown(" ")
if st.button("✅ Continue to the app"):
    st.switch_page("pages/Home.py")  # Change this to your actual homepage file if needed
    
