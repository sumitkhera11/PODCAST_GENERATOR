import os
import time
import requests
from dotenv import load_dotenv
import streamlit as st
from blog_summarizer import summarize_blog

# =============================
# ENV
# =============================
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Default ElevenLabs voice

# =============================
# CUSTOM CSS
# =============================
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #0f172a, #020617);
        color: white;
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        max-width: 900px;
        margin: auto;
        padding: 30px;
    }
    h1 {
        text-align: center;
        font-size: 2.4rem;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    p {
        color: #94a3b8;
        font-size: 1rem;
        text-align: center;
    }
    .card {
        background: #020617;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.5);
        border: 1px solid #1e293b;
        margin-bottom: 20px;
    }
    button {
        background: linear-gradient(90deg, #6366f1, #3b82f6);
        border-radius: 12px;
        font-weight: 600;
        padding: 12px;
        color: white;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True
)

# =============================
# AUDIO GENERATION
# =============================
def generate_audio(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY,
    }

    payload = {
        "text": text,
        "model_id": "eleven_flash_v2_5",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"ElevenLabs API error {response.status_code}: {response.text}")

    audio_path = "podcast.mp3"
    with open(audio_path, "wb") as f:
        f.write(response.content)

    return audio_path

# =============================
# STREAMLIT UI
# =============================
st.title("🎙️ AI Podcast Generator")
st.write("Turn any blog into a professional podcast using AI summarization and voice synthesis")

with st.form(key="podcast_form"):
    url_input = st.text_input("🔗 Blog URL", placeholder="https://example.com/blog-post")
    submit_btn = st.form_submit_button("🚀 Generate Podcast")

if submit_btn:
    if not url_input.strip():
        st.error("❌ Please enter a valid blog URL.")
    else:
        try:
            status_text = st.empty()
            status_text.info("🔍 Scraping & summarizing blog...")
            summary = summarize_blog(url_input)
            time.sleep(0.5)

            status_text.info("🎧 Generating podcast audio...")
            audio_path = generate_audio(summary[:1200])
            time.sleep(0.5)

            status_text.success("✅ Podcast generated successfully!")

            st.subheader("📝 Blog Summary")
            st.text_area("", value=summary, height=200)

            st.subheader("🔊 Podcast Audio")
            st.audio(audio_path)

        except Exception as e:
            status_text.error(f"❌ Error: {str(e)}")
