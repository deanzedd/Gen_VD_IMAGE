# GEN VIDEO, TEXT, AUDIO, IMAGE

## GEN VIDEO from IMAGE

1. **Download Library**
    ```bash
    pip install -r requirements.txt
    ```

2. **export API key**
    ```bash
    export GEMINI_API_KEY="your_key
    ```
3. **Generate video**
    ```bash
    cd Gen_vd
    # Tạo video (script mặc định)
    python main.py
    ```

    or
    ```bash
    cd Gen_vd
    # Tạo video (script qua litellm + Gemini TTS)
    python main.py --use_litellm --prefer_gemini
    ```

