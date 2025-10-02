from config import SCRIPT_OUT, OUTPUT_DIR
from pathlib import Path

# litellm (optional)
try:
    from litellm import completion
    _HAS_LITELLM = True
except Exception:
    _HAS_LITELLM = False

DEFAULT_SCRIPT = """
Xin chào quý vị, chào mừng quý vị đến với bản tin đặc biệt hôm nay trên kênh VTV.
...
Và xin được nhắc lại: đây là sản phẩm của cuộc thi AI Thực Chiến.
"""

def generate_script(use_litellm=False, prompt=None):
    text = DEFAULT_SCRIPT
    if use_litellm and _HAS_LITELLM:
        try:
            resp = completion(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Bạn là biên tập viên VTV"},
                    {"role": "user", "content": prompt or "Viết kịch bản 3 phút về kỷ niệm 80 năm Quốc khánh 2/9/2025."}
                ],
                max_tokens=800
            )
            text = resp["choices"][0]["message"]["content"]
        except Exception as e:
            print("⚠️ litellm lỗi, dùng script mặc định:", e)

    if "đây là sản phẩm của cuộc thi AI Thực Chiến" not in text:
        text += "\n\nVà xin được nhắc lại: đây là sản phẩm của cuộc thi AI Thực Chiến.\n"

    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    with open(SCRIPT_OUT, "w", encoding="utf-8") as f:
        f.write(text)

    return str(SCRIPT_OUT), text