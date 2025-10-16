# Review Tiên giới — Webapp (customized)

This project is a mobile-friendly web application that generates short review videos from text sections.
It uses Flask + gTTS + MoviePy to synthesize speech and create slides.
Configured with dark theme and female-voice preference.

## Quick Start (local)
1. Install ffmpeg (required).
2. Create virtualenv and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run:
   ```
   python app.py
   ```
4. Open on your phone: `http://<server-ip>:5000/` and use the web interface.

## Notes
- Place optional background images into `assets/backgrounds/` and music in `assets/music/`.
- For more natural voices replace gTTS with ElevenLabs or Google Cloud TTS (API key required).
