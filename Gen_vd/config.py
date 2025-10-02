import os
from pathlib import Path

# Video config
W, H = 1920, 1080
FPS = 24
DURATION = 180.0  # giây

# API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_ENDPOINT = os.getenv("GEMINI_ENDPOINT")

# Paths
ASSETS_DIR = Path("assets")
OUTPUT_DIR = Path("output")
IMAGES_DIR = ASSETS_DIR / "images"
HOST_IMG = ASSETS_DIR / "host.png"
SCRIPT_OUT = OUTPUT_DIR / "script.txt"
TTS_OUT = OUTPUT_DIR / "tts.wav"
VIDEO_OUT = OUTPUT_DIR / "video.mp4"