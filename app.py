# app.py (customized for 'Review Tiên giới' - dark theme, female voice preference)
import os
import uuid
import json
import tempfile
from pathlib import Path
from flask import Flask, render_template, request, send_from_directory, jsonify
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, TextClip, afx
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_BG = BASE_DIR / "assets" / "backgrounds"
ASSETS_MUSIC = BASE_DIR / "assets" / "music"
FONT_PATH = None  # đặt đường dẫn tới ttf nếu muốn

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ASSETS_BG, exist_ok=True)
os.makedirs(ASSETS_MUSIC, exist_ok=True)

app = Flask(__name__, static_folder="static", template_folder="templates")

def make_slide_image(text, heading=None, size=(1280,720)):
    bg_files = [p for p in ASSETS_BG.glob("*") if p.suffix.lower() in (".jpg",".png")]
    if bg_files:
        bg = Image.open(bg_files[0]).convert("RGBA").resize(size)
    else:
        bg = Image.new("RGBA", size, (6,10,18,255))
    draw = ImageDraw.Draw(bg)
    try:
        font_h = ImageFont.truetype(FONT_PATH or "DejaVuSans-Bold.ttf", 48)
        font_t = ImageFont.truetype(FONT_PATH or "DejaVuSans.ttf", 28)
    except Exception:
        font_h = ImageFont.load_default()
        font_t = ImageFont.load_default()
    x_margin = 40
    y = 40
    if heading:
        draw.text((x_margin,y), heading, fill=(255,200,90), font=font_h)
        y += 70
    lines = []
    words = text.split()
    line = ""
    for w in words:
        if len(line) + len(w) +1 > 40:
            lines.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    if line: lines.append(line)
    for i, ln in enumerate(lines[:12]):
        draw.text((x_margin, y + i*38), ln, fill=(230,230,230), font=font_t)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png", dir=OUTPUT_DIR)
    bg.convert("RGB").save(tmp.name, "PNG")
    return tmp.name

def synthesize_gtts(text, lang="vi", out_path=None):
    # gTTS doesn't allow specifying gender; Google will pick a voice.
    tts = gTTS(text=text, lang=lang, slow=False)
    if not out_path:
        out_path = str(OUTPUT_DIR / f"{uuid.uuid4()}.mp3")
    tts.save(out_path)
    return out_path

def build_video(sections, title="Review Tiên giới", voice_lang="vi"):
    clips = []
    for sec in sections:
        heading = sec.get("heading")
        text = sec.get("text", "")
        words = text.split()
        chunk_size = 120
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size])
            if not chunk.strip():
                continue
            img_path = make_slide_image(chunk, heading if i==0 else None)
            audio_path = synthesize_gtts(chunk, lang=voice_lang)
            audio_clip = AudioFileClip(audio_path)
            img_clip = ImageClip(img_path).set_duration(audio_clip.duration).resize((1280,720))
            txt = TextClip(chunk, fontsize=28, method="caption", size=(1280-80, None), align='West')
            txt = txt.set_position(('center', 720-140)).set_duration(audio_clip.duration)
            composite = CompositeVideoClip([img_clip, txt]).set_audio(audio_clip)
            clips.append(composite)
    if not clips:
        raise RuntimeError("No clips to render")
    final = concatenate_videoclips(clips, method="compose")
    out_name = f"{uuid.uuid4()}.mp4"
    out_path = OUTPUT_DIR / out_name
    final.write_videofile(str(out_path), fps=24, codec="libx264", audio_codec="aac")
    return out_name

@app.route("/")
def index():
    return render_template("index.html", app_title="Review Tiên giới")

@app.route("/create", methods=["POST"])
def create():
    payload = request.json
    try:
        title = payload.get("title", "Review Tiên giới")
        sections = payload.get("sections", [])
        voice = payload.get("voice", "vi")
        out_file = build_video(sections, title=title, voice_lang=voice)
        return jsonify({"ok": True, "file": out_file})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
