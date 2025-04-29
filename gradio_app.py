import gradio as gr

from gradio_audio import app_tts
from gradio_video import app_video

# Create Gradio interface
with gr.Blocks(title="AvatarX") as app:
    gr.Markdown(
    """
    <h1 align="center">AvatarX</h1>
    <div style="display:flex;justify-content:center;column-gap:4px;">
        <a href="https://github.com/bestilyq/AvatarX">
            <img src='https://img.shields.io/badge/GitHub-Repo-blue'>
        </a> 
        <a href="https://arxiv.org/abs/2412.09262">
            <img src='https://img.shields.io/badge/arXiv-Paper-red'>
        </a>
    </div>
    <h2 align="center">A digital human built with LatentSync and F5-TTS</h2>
    <style> video { max-height: 500px; } </style>
    """
    )

    gr.TabbedInterface(
        [app_tts, app_video],
        ["F5-TTS", "LatentSync"],
    )

if __name__ == "__main__":
    app.launch(inbrowser=True, share=True)
