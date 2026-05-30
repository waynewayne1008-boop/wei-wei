from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
import json

app = Flask(__name__)

# ── 安全防護 ──
# 建議做法：從電腦環境變數中讀取 API Key (推薦)
# 如果你暫時不會設定環境變數，可以先把 os.environ.get(...) 換成 "你的_API_KEY_字串"
# 但請記得，上傳到 GitHub 前一定要拿掉！
API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

# 加入設定，讓 AI 每次的回答都有隨機性
generation_config = {
    "temperature": 1.0,  # 數字越高，AI 越隨機、越不會重複（範圍 0.0 ~ 2.0）
}

model = genai.GenerativeModel(
    model_name="gemini-3.5-flash",
    generation_config=generation_config
)

LANGUAGE = "流行用語"

@app.route("/")
def home():
    # 讓 Flask 自動去 templates 資料夾找 index.html 並呈現給使用者
    return render_template("index.html")

@app.route("/api/make_card", methods=["POST"])
def make_card():
    # 原本寫在前端的 Prompt（提示詞），現在安全的待在後端
    prompt = f"""請幫我出一張{LANGUAGE}學習小卡，回應請用 JSON：
{{
  "word": "（一個常用詞或片語）",
  "pinyin": "（發音標記）",
  "meaning": "（中文意思，含使用情境，30字內）",
  "example": "（一句例句）"
}}
不要加 markdown 標記，直接給 JSON。"""

    try:
        # 向 Google Gemini 伺服器發送請求
        response = model.generate_content(prompt)
        text = response.text
        
        # 預防 AI 自作主張加入 ```json 標籤，與你原本的前端防錯邏輯相同
        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "").strip()
            
        # 解析成 Python 字典，確保格式正確
        card_data = json.loads(text)
        
        # 回傳給前端網頁
        return jsonify(card_data)
        
    except Exception as e:
        # 如果後端發生錯誤，回傳錯誤訊息給前端
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
