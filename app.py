import os
import json
from datetime import datetime

import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI


# -----------------------------
# Memory Functions
# -----------------------------
MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


# -----------------------------
# Helper Functions
# -----------------------------
def extract_video_id(url: str) -> str:
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    else:
        return url.strip()

def get_transcript(video_id: str) -> str:
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join([item["text"] for item in transcript])


def summarize_with_openai(api_key: str, transcript: str) -> str:
    client = OpenAI(api_key=api_key)

    prompt = f"""
You are an expert assistant that summarizes YouTube videos.

Instructions:
- Summarize clearly and concisely
- Use bullet points
- Highlight key ideas and takeaways
- Keep it easy to read

Transcript:
{transcript}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You summarize YouTube transcripts."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="🎥 ➡️ 📝 YouTube Summary Agent")
st.title("🎥 ➡️ 📝 YouTube Summary Agent")
st.write("Paste a YouTube link and get a clean AI-generated summary.")

memory = load_memory()

# Sidebar
st.sidebar.header("🔑 API Key")
openai_key = st.sidebar.text_input("OpenAI API Key", type="password")

# Input
youtube_url = st.text_input("Enter YouTube URL")

# Button
if st.button("Generate Summary", disabled=not openai_key):
    if not youtube_url.strip():
        st.warning("Please enter a YouTube URL.")
    else:
        try:
            with st.spinner("Fetching transcript and generating summary..."):

                video_id = extract_video_id(youtube_url)
                try:
                    transcript_text = get_transcript(video_id)
                except Exception as e:
                    st.error("Unable to fetch transcript for this video. Sometimes YouTube captions are unavailable.")
                    st.caption(f"Details: {e}")
                    transcript_text = None

                summary = summarize_with_openai(openai_key, transcript_text)

                # Save to memory if new
                existing_urls = {item["url"] for item in memory}
                if youtube_url not in existing_urls:
                    memory.append({
                        "url": youtube_url,
                        "summary": summary,
                        "timestamp": datetime.now().isoformat()
                    })
                    save_memory(memory)
                else:
                    st.info("This video already exists in memory.")

                st.success("Summary generated!")
                st.subheader("📝 Summary")
                st.write(summary)

        except Exception as e:
            st.error(f"Error: {e}")


# -----------------------------
# Show Memory
# -----------------------------
st.divider()
st.subheader("📚 Previous Summaries")

if memory:
    for item in reversed(memory[-10:]):
        st.markdown(f"**{item['url']}**")
        st.caption(item["timestamp"])
        st.write(item["summary"])
        st.divider()
else:
    st.write("No summaries saved yet.")
