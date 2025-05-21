import streamlit as st
import json
import os
from datetime import datetime
import pytz


DATA_FILE = "forum_feedback.json"

# Load existing messages
def load_messages():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return []

# Save messages to JSON
def save_messages(messages):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2)

# Add new message
def add_message(name, email, message):
    messages = load_messages()
    eastern = pytz.timezone("America/New_York")
    now_eastern = datetime.now(eastern)
    messages.append({
        "name": name,
        "email": email,
        "message": message,
        "timestamp": now_eastern.strftime("%Y-%m-%d %H:%M:%S"),
        "reply": None
    })
    save_messages(messages)


# Add reply to a message
def reply_to_message(index, reply):
    messages = load_messages()
    messages[index]["reply"] = reply
    save_messages(messages)

# Streamlit app
def forum_page():
    st.title("💬 Feedback Forum")

    with st.form("feedback_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        message = st.text_area("Your Message")
        submitted = st.form_submit_button("Submit")

        if submitted and name and message:
            add_message(name, email, message)
            st.success("✅ Message sent successfully!")

    st.markdown("---")
    st.subheader("📨 Previous Feedback")

    messages = load_messages()
    if not messages:
        st.info("No messages yet. Be the first to write!")
    else:
        for i, msg in enumerate(reversed(messages)):
            idx = len(messages) - 1 - i  # to keep correct index
            with st.expander(f"🧾 {msg['name']} ({msg['timestamp']})"):
                st.write(msg["message"])
                st.caption(f"📧 {msg['email']}")

                if msg["reply"]:
                    st.success(f"💬 Admin reply: {msg['reply']}")
                else:
                    # Optional: only allow admin to reply
                    with st.form(f"reply_form_{i}"):
                        admin_reply = st.text_input("Reply as Admin")
                        reply_submit = st.form_submit_button("Send Reply")
                        if reply_submit and admin_reply:
                            reply_to_message(idx, admin_reply)
                            st.success("✅ Reply sent!")


if __name__ == "__main__":
    forum_page()
