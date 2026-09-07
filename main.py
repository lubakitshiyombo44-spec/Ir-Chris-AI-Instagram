import os
from flask import Flask, request
from groq import Groq

app = Flask(__name__)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "ir_chris_2026")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

@app.route("/")
def home():
    return "Bot Instagram Ir Chris en ligne ✅"

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Failed", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    print(request.get_json())
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
