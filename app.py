import os
import json
from datetime import datetime

import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from agno.agent import Agent
from agno.models.openai import OpenAIChat


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


# -----------------------------
# Streamlit Page Config
# -----------------------------
st.set_page_config(page_title="🎥 ➡️ 📝 YouTube Summary Agent")
st.title("🎥 ➡️ 📝 YouTube Summary Agent")
st.write("Paste a YouTube link and get a clean AI-generated summary.")

# Load memory
memory = load_memory()


# -----------------------------
# Sidebar - API Key Input
# -----------------------------
st.sidebar.header("🔑 API Key")
openai_key = st.sidebar.text_input("OpenAI API Key", type="password")


# -----------------------------
# Main Input
# -----------------------------
youtube_url = st.text_input("Enter YouTube URL")


# -----------------------------
# Button Action
# -----------------------------
if st.button("Generate Summary", disabled=not openai_key):
    if not youtube_url.strip():
        st.warning("Please enter a YouTube URL.")
    else:
        try:
            with st.spinner("Fetching transcript and generating summary..."):

                # Set API key
                os.environ["OPENAI_API_KEY"] = openai_key

                # Extract transcript
                video_id = extract_video_id(youtube_url)
                transcript_text = get_transcript(video_id)

                # Create Agent
                agent = Agent(
                    name="YouTube Summarizer",
                    model=OpenAIChat(id="gpt-4o"),
                    instructions=[
                        "Summarize this YouTube transcript clearly and concisely.",
                        "Use bullet points.",
                        "Highlight the key ideas and takeaways.",
                        "Keep it easy to read."
                    ],
                )

                # Run Agent
                response = agent.run(transcript_text)
                summary = response.content

                # Save to memory if not duplicate
                existing_urls = {item["url"] for item in memory}

                if youtube_url not in existing_urls:
                    memory.append({
                        "url": youtube_url,
                        "summary": summary,
                        "timestamp": datetime.now().isoformat()
                    })
                    save_memory(memory)
                else:
                    st.info("This video is already saved. Showing existing summary.")

                # Display result
                st.success("Summary generated!")
                st.subheader("📝 Summary")
                st.write(summary)

        except Exception as e:
            st.error(f"Error: {e}")


# -----------------------------
# Memory Display
# -----------------------------
st.divider()
st.subheader("📚 Previous Summaries")

if memory:
    for item in reversed(memory[-10:]):  # Show last 10
        st.markdown(f"**{item['url']}**")
        st.caption(item["timestamp"])
        st.write(item["summary"])
        st.divider()
else:
    st.write("No summaries saved yet.")
