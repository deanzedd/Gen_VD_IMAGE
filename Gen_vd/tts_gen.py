import os, requests
from gtts import gTTS
from pydub import AudioSegment
from pathlib import Path
from config import GEMINI_API_KEY, GEMINI_ENDPOINT

# Google Generative AI (optional)
try:
    import google.generativeai as genai
    _HAS_GENAI = True
except:
    _HAS_GENAI = False

def tts_gemini_sdk(text, out_wav):
    genai.configure(api_key=GEMINI_API_KEY)
    audio_bytes = genai.audio.speech.create(model="gemini-pro-tts", voice="alloy", input=text)
    with open(out_wav, "wb") as f:
        f.write(audio_bytes)
    return out_wav

def tts_http(text, out_wav):
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}", "Content-Type": "application/json"}
    payload = {"input": text, "voice": "default", "format": "wav"}
    r = requests.post(GEMINI_ENDPOINT, json=payload, headers=headers, timeout=60)
    r.raise_for_status()
    with open(out_wav, "wb") as f:
        f.write(r.content)
    return out_wav

def tts_gtts(text, out_wav):
    tmp = str(out_wav) + ".mp3"
    gTTS(text=text, lang="vi").save(tmp)
    audio = AudioSegment.from_mp3(tmp).set_frame_rate(48000).set_channels(2)
    audio.export(out_wav, format="wav")
    os.remove(tmp)
    return out_wav

def generate_tts(text, out_wav, prefer_gemini=True):
    Path(out_wav).parent.mkdir(parents=True, exist_ok=True)
    if prefer_gemini and GEMINI_API_KEY:
        try:
            if _HAS_GENAI:
                return tts_gemini_sdk(text, out_wav)
            return tts_http(text, out_wav)
        except Exception as e:
            print("⚠️ Gemini lỗi, fallback gTTS:", e)
    return tts_gtts(text, out_wav)
