# vtv_news_generator.py
# One-file pipeline to generate a 3-minute VTV-style news video
# Requirements: moviepy, numpy, pydub, gTTS, Pillow, requests, tqdm, python-dotenv, google-generativeai (optional)

import os
import requests
import argparse
from gtts import gTTS
from pydub import AudioSegment
from moviepy.editor import (ImageClip, AudioFileClip, CompositeVideoClip,
                            TextClip, ColorClip)
from PIL import Image
import numpy as np
# ==============================
# Gemini Wrapper
# ==============================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_ENDPOINT = os.getenv("GEMINI_ENDPOINT")

try:
    import google.generativeai as genai
    _HAS_GENAI = True
except Exception:
    _HAS_GENAI = False


def tts_via_http(text, out_wav, voice="default"):
    if not GEMINI_ENDPOINT:
        raise RuntimeError("Set GEMINI_ENDPOINT to use HTTP Gemini TTS")
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}",
               "Content-Type": "application/json"}
    payload = {"input": text, "voice": voice, "format": "wav"}
    r = requests.post(GEMINI_ENDPOINT, json=payload, headers=headers, timeout=60)
    r.raise_for_status()
    with open(out_wav, "wb") as f:
        f.write(r.content)
    return out_wav


def tts_via_genai(text, out_wav, model="gemini-pro-tts", voice="alloy"):
    if not _HAS_GENAI:
        raise RuntimeError("google.generativeai not installed")
    genai.configure(api_key=GEMINI_API_KEY)
    audio_bytes = genai.audio.speech.create(model=model, voice=voice, input=text)
    with open(out_wav, "wb") as f:
        f.write(audio_bytes)
    return out_wav

def generate_tts(text, out_wav, prefer="gemini"):
    if GEMINI_API_KEY:
        if prefer == "genai" and _HAS_GENAI:
            return tts_via_genai(text, out_wav)
        else:
            return tts_via_http(text, out_wav)
    else:
        print("GEMINI_API_KEY not set, using gTTS instead")
        tts = gTTS(text, lang='vi')

# ==============================
# Script Generator
# ==============================
SCRIPT_TEXT = '''Xin chào quý vị, chào mừng quý vị đến với bản tin đặc biệt hôm nay trên kênh VTV.
Trong chương trình này chúng ta sẽ tổng kết và phân tích các hoạt động chào mừng kỷ niệm 80 năm Quốc khánh 2 tháng 9 năm 2025 trên khắp cả nước.

(Cảnh: giới thiệu nhanh các hoạt động chính: lễ diễu binh, lễ viếng, giao lưu văn hóa, triển lãm...) 

Đoạn phóng sự 1: Lễ kỷ niệm tại Hà Nội, những hình ảnh nổi bật, ý nghĩa của các hoạt động.

Đoạn phóng sự 2: Hoạt động tại các tỉnh, sự tham gia của cộng đồng và các tổ chức.

Phân tích: Tác động xã hội, văn hóa và tinh thần của chuỗi hoạt động mừng Quốc khánh 2/9/2025.

Kết luận: Sự lan tỏa tinh thần, những bài học và hướng phát triển trong tương lai.

Và xin được nhắc lại: đây là sản phẩm của cuộc thi AI Thực Chiến.

Xin cảm ơn quý vị đã theo dõi. Hẹn gặp lại trong bản tin tiếp theo.
'''

# ==============================
# Video Builder
# ==============================
W, H = 1920, 1080
DURATION = 180
FPS = 24


def build_video(images_dir, audio_path, out_path):
    img_files = sorted([os.path.join(images_dir, f) for f in os.listdir(images_dir)
                        if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    if not img_files:
        raise RuntimeError("No images found in assets/images")

    audio = AudioFileClip(audio_path)
    audio_duration = audio.duration

    seg_dur = audio_duration / len(img_files)
    clips = []
    from moviepy.editor import vfx
    for img in img_files:
        c = ImageClip(img).set_duration(seg_dur)
        c = c.resize(height=H)
        if c.w < W:
            c = c.resize(width=W)
        c = c.fx(vfx.fadein, 1).fx(vfx.fadeout, 1)
        clips.append(c)

    slideshow = CompositeVideoClip(clips).set_duration(audio_duration)

    # MC ảo
    host_img = "assets/host.png"
    host_clip = None
    if os.path.exists(host_img):
        hc = ImageClip(host_img).set_duration(audio_duration)
        hc = hc.resize(height=600).set_position((W - 650, H - 700))
        host_clip = hc

    # Lower third
    txt = TextClip("BẢN TIN ĐẶC BIỆT - VTV", fontsize=60, color="white", bg_color="red", size=(W, 100))
    txt = txt.set_position(("center", H - 120)).set_duration(audio_duration)

    final_clips = [slideshow, txt]
    if host_clip:
        final_clips.append(host_clip)

    final = CompositeVideoClip(final_clips, size=(W, H)).set_audio(audio)
    final.write_videofile(out_path, fps=FPS, codec="libx264", audio_codec="aac")


# ==============================
# Main Pipeline
# ==============================
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--images", default="assets/images")
    parser.add_argument("--out", default="output/video.mp4")
    parser.add_argument("--script", default="output/script.txt")
    parser.add_argument("--tts", default="output/tts.wav")
    args = parser.parse_args()

    os.makedirs("output", exist_ok=True)

    # Save script
    with open(args.script, "w", encoding="utf-8") as f:
        f.write(SCRIPT_TEXT)
    print("Script saved to", args.script)

    # TTS
    print("Generating TTS...")
    generate_tts(SCRIPT_TEXT, args.tts)

    # Video
    print("Building video...")
    build_video(args.images, args.tts, args.out)
    print("Video saved to", args.out)