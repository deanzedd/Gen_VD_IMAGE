import litellm
import json
import os
import base64
import re

AI_API_BASE = "https://api.thucchien.ai"
AI_API_KEY = "sk-_M2s7MMcTlAoMtAVR8ybNQ"

litellm.api_base = AI_API_BASE

#các tham số động
content = "câu chuyện ông lão đánh cá và con cá vàng" #nội dung vid
n = 10 #số scene
time = "8s" #tgian mỗi scene
style = "chibi đáng yêu" #phong cách nhân vật

prompt = f"""
Hãy viết kịch bản ngắn gồm {n} cảnh kể về {content}. 
Kết quả trả về phải là **JSON object** với 2 key:

- "characters": danh sách nhân vật kèm các trạng thái có thể xuất hiện trong câu chuyện.
  Mỗi biến thể trạng thái được xem như một nhân vật riêng và có:
  - "id": mã duy nhất viết thường không dấu, dạng <ten_nhan_vat>__<trang_thai>, 
          ví dụ "ba_lao__ngheo_kho", "ba_lao__giau_co", "ong_lao__binh_thuong"
  - "name": tên hiển thị, ví dụ "Bà Lão (nghèo khổ)"
  - "description": mô tả ngoại hình/đặc điểm nhận diện ở trạng thái đó 
                   để dùng làm tham chiếu tạo ảnh (ví dụ: "quần áo rách rưới, mặt cau có")

- "script": danh sách {n} cảnh, mỗi cảnh có:
  - "scene": số thứ tự cảnh
  - "description": mô tả cảnh (giới hạn trong khoảng {time})
  - "dialogues": danh sách hội thoại dạng [{{ "character": <character_id>, "line": ... }}]
    - "character" ở đây chỉ tham chiếu tới id trong danh sách characters phía trên.

Trả về kết quả **chỉ dưới dạng JSON object**.
"""

def clean_json_str(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z0-9]*\n?", "", s)
        s = re.sub(r"```$", "", s.strip())
    return s

if os.path.exists('data.json'):
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
else:
    response = litellm.completion(
      model="litellm_proxy/gemini-2.5-pro",
      messages=[{"role": "user", "content": prompt}],
      api_key=AI_API_KEY
    )
    data_str = clean_json_str(response.choices[0].message["content"])
    data = json.loads(data_str)
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

characters = data["characters"]
script = data["script"]

print(characters)

#sinh ảnh nhân vật
os.makedirs("characters", exist_ok=True)

for charac in characters:
    ref_image_b64 = None

    # Nếu đã có ảnh gốc → dùng làm reference
    if "image" in charac and os.path.exists(charac["image"]):
        with open(charac["image"], "rb") as f:
            ref_image_b64 = base64.b64encode(f.read()).decode("utf-8")

    if ref_image_b64:
        response = litellm.image_generation(
            prompt=f"Giữ nguyên phong cách {style}, giữ khuôn mặt giống ảnh tham chiếu. "
                   f"Chỉ vẽ nhân vật {charac['name']} ({charac['id']}). "
                   f"Mô tả: {charac['description']}. "
                   f"Nền trắng tinh, không có chi tiết phụ.",
            model="litellm_proxy/imagen-4",
            n=1,
            api_key=AI_API_KEY,
            api_base=AI_API_BASE,
            referenced_image_ids=[ref_image_b64]
        )
    else:
        # text2img lần đầu
        response = litellm.image_generation(
            prompt=f"Vẽ nhân vật {charac['name']} ({charac['id']}) "
                   f"theo phong cách {style}. "
                   f"Mô tả: {charac['description']}. "
                   f"Chỉ phác họa nhân vật toàn thân, nền trắng tinh, không thêm chi tiết nền.",
            model="litellm_proxy/imagen-4",
            n=1,
            api_key=AI_API_KEY,
            api_base=AI_API_BASE,
        )
    image_obj = response.data[0]
    b64_data = image_obj['b64_json']
    image_data = base64.b64decode(b64_data)
    save_path = f"characters/{charac['id']}.png"
    with open(save_path, 'wb') as f:
        f.write(image_data)
    charac["image"] = save_path
    print(f"Image saved to {save_path}")

#ghi lại file data.json update cả path đến ảnh
with open("data.json", "w", encoding="utf-8") as f:
    json.dump({"characters": characters, "script": script}, f, ensure_ascii=False, indent=2)