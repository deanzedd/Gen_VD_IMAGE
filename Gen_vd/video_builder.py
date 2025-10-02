from pathlib import Path
from moviepy.editor import (ImageClip, AudioFileClip, CompositeVideoClip,
                            TextClip, concatenate_videoclips, vfx)
from config import W, H, FPS, DURATION

def build_video(images_dir, audio_path, out_path, host_image=None):
    images = sorted([str(p) for p in Path(images_dir).glob("*") if p.suffix.lower() in [".jpg",".png"]])
    if not images:
        raise RuntimeError("❌ Không tìm thấy ảnh trong " + str(images_dir))

    audio = AudioFileClip(audio_path).subclip(0, DURATION)
    seg_dur = DURATION / len(images)

    clips = []
    for img in images:
        c = ImageClip(img).set_duration(seg_dur)
        c = c.resize(height=H)
        if c.w < W: c = c.resize(width=W)
        c = c.fx(vfx.fadein, 1).fx(vfx.fadeout, 1)
        clips.append(c)

    slideshow = concatenate_videoclips(clips, method="compose").set_duration(DURATION)

    overlays = [slideshow]

    # Host
    if host_image and Path(host_image).exists():
        host = ImageClip(str(host_image)).set_duration(DURATION)
        host = host.resize(height=int(H*0.55)).set_position((W-650, H-700))
        overlays.append(host)

    # Title bar
    title = TextClip("BẢN TIN ĐẶC BIỆT - VTV", fontsize=50, color="white", bg_color="red", size=(W,100))
    title = title.set_position(("center", H-120)).set_duration(DURATION)
    overlays.append(title)

    # Mandatory text
    mandatory = TextClip("Đây là sản phẩm của cuộc thi AI Thực Chiến", fontsize=36, color="white", bg_color="red")
    mandatory = mandatory.set_start(10).set_duration(6).set_position(("center", H-200))
    overlays.append(mandatory)

    final = CompositeVideoClip(overlays, size=(W,H)).set_audio(audio)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    final.write_videofile(str(out_path), fps=FPS, codec="libx264", audio_codec="aac")
