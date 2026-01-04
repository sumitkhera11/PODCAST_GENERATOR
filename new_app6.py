import os
import time
import requests
import gradio as gr
from dotenv import load_dotenv

# Create Agent → Create Task → Pass to Crew → Run
from blog_summarizer import summarize_blog

# =============================
# ENV
# =============================
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Default ElevenLabs voice
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"

# =============================
# CUSTOM CSS
# =============================
CUSTOM_CSS = """
body {
    background: linear-gradient(135deg, #0f172a, #020617);
    color: white;
    font-family: 'Inter', sans-serif;
}

#app-container {
    max-width: 900px;
    margin: auto;
    padding: 30px;
}

.header {
    text-align: center;
    margin-bottom: 30px;
}

.header h1 {
    font-size: 2.4rem;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.header p {
    color: #94a3b8;
    font-size: 1rem;
}

.card {
    background: #020617;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.5);
    border: 1px solid #1e293b;
    margin-bottom: 20px;
}

.gr-button-primary {
    background: linear-gradient(90deg, #6366f1, #3b82f6);
    border-radius: 12px;
    font-weight: 600;
    padding: 12px;
}

.gr-button-primary:hover {
    transform: scale(1.02);
}

.status-box textarea {
    background: #020617 !important;
    color: #22c55e !important;
    border-radius: 10px;
    border: 1px solid #1e293b;
}
"""

# =============================
# AUDIO GENERATION (REST)
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
# MAIN PIPELINE
# =============================
def process_url(url, progress=gr.Progress()):
    try:
        progress(0.1, desc="🔍 Scraping & summarizing blog...")
        summary = summarize_blog(url)
        time.sleep(0.5)

        progress(0.6, desc="🎧 Generating podcast audio...")
        audio_path = generate_audio(summary[:1200])
        time.sleep(0.5)

        progress(1.0, desc="✅ Podcast ready!")
        return summary, audio_path, "✅ Podcast generated successfully"

    except Exception as e:
        return "", None, f"❌ Error: {str(e)}"


# =============================
# 🎨 GRADIO UI
# =============================
with gr.Blocks(css=CUSTOM_CSS, title="AI Podcast Generator") as demo:
    with gr.Column(elem_id="app-container"):

        # ---------- HEADER ----------
        gr.HTML("""
        <div class="header">
            <h1>🎙️ AI Podcast Generator</h1>
            <p>Turn any blog into a professional podcast using AI summarization and voice synthesis</p>
        </div>
        """)

        # ---------- INPUT CARD ----------
        with gr.Column(elem_classes="card"):
            url_input = gr.Textbox(
                label="🔗 Blog URL",
                placeholder="https://example.com/blog-post",
            )

            generate_btn = gr.Button(
                "🚀 Generate Podcast",
                variant="primary"
            )

            status_output = gr.Textbox(
                label="Status",
                lines=1,
                interactive=False,
                elem_classes="status-box"
            )

        # ---------- OUTPUT CARD ----------
        with gr.Column(elem_classes="card"):
            gr.Markdown("### 📝 Blog Summary")
            summary_output = gr.Textbox(lines=10)

            gr.Markdown("### 🔊 Podcast Audio")
            audio_output = gr.Audio(type="filepath")

        # ---------- ACTION ----------
        generate_btn.click(
            fn=process_url,
            inputs=[url_input],
            outputs=[summary_output, audio_output, status_output],
        )


if __name__ == "__main__":
    demo.launch()
