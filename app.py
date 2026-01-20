import os
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from agno.agent import Agent
from agno.models.openai import OpenAIChat

# -----------------------------
# Streamlit Page Config
# -----------------------------
st.set_page_config(page_title="🎥 ➡️ 📝 YouTube Summary Agent")
st.title("🎥 ➡️ 📝 YouTube Summary Agent")

st.write("Paste a YouTube link and get a clean AI-generated summary.")

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
# Helper Functions
# -----------------------------
def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from URL."""
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    else:
        return url.strip()

def get_transcript(video_id: str) -> str:
    """Fetch transcript text from YouTube."""
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join([item["text"] for item in transcript])

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

                # Display Output
                st.success("Summary generated!")
                st.subheader("📝 Summary")
                st.write(summary)

        except Exception as e:
            st.error(f"Error: {e}")
