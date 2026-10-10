import os
import requests
from flask import Flask, request
from google import genai

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = (
    "انت مساعد بترد نيابة عن صاحب الحساب على رسائل تليجرام. "
    "رد بشكل مختصر، ودود، وباللهجة المصرية."
)


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text")

    if chat_id and text:
        try:
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=f"{SYSTEM_PROMPT}\n\nرسالة العميل: {text}",
            )
            reply = response.text or "تمام."
        except Exception:
            reply = "حصل خطأ بسيط، هرد عليك بنفسي قريب."

        requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json={"chat_id": chat_id, "text": reply},
            timeout=15,
        )

    return "ok"


@app.route("/")
def home():
    return "Bot is running"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
