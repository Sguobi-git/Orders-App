# feedback_page.py
import streamlit as st
from datetime import datetime
import os

def feedback_page():
    st.title("💬 Send us your Feedback or Questions")

    st.write("We value your opinion! Fill out the form below to get in touch with us.")

    with st.form("feedback_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        message = st.text_area("Your Message", height=150)
        submitted = st.form_submit_button("Send")

        if submitted:
            # Save to a text file (or change to saving to database / Google Sheet)
            with open("feedback_messages.txt", "a") as f:
                f.write(f"\n---\nDate: {datetime.now()}\nName: {name}\nEmail: {email}\nMessage: {message}\n")
            
            st.success("✅ Thank you for your message! We'll get back to you soon.")
