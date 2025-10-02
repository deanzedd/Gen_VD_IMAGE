import argparse
from config import *
from script_gen import generate_script
from tts_gen import generate_tts
from video_builder import build_video

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--use_litellm", action="store_true")
    parser.add_argument("--prefer_gemini", action="store_true")
    args = parser.parse_args()

    # 1) Script
    script_file, text = generate_script(use_litellm=args.use_litellm)
    print("✅ Script saved:", script_file)

    # 2) TTS
    generate_tts(text, TTS_OUT, prefer_gemini=args.prefer_gemini)
    print("✅ Audio saved:", TTS_OUT)

    # 3) Video
    build_video(IMAGES_DIR, TTS_OUT, VIDEO_OUT, host_image=HOST_IMG)
    print("✅ Video saved:", VIDEO_OUT)

if __name__ == "__main__":
    main()
