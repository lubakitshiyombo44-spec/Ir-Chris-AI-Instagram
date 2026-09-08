from flask import Flask, request
import os, requests

app = Flask(__name__)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "Chris2026")
PAGE_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

@app.route('/')
def home():
    return "Ir Chris AI Bot Online"

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Token invalide", 403

@app.route('/webhook', methods=['POST'])
def handle_message():
    data = request.get_json()
    print(data) # Tu verras les messages arriver dans les Logs Railway
    
    # Gestion Instagram + Facebook
    if 'entry' in data:
        for entry in data['entry']:
            if 'messaging' in entry:
                for msg in entry['messaging']:
                    sender = msg['sender']['id']
                    if 'message' in msg and 'text' in msg['message']:
                        text = msg['message']['text']
                        # Ici tu appelles ton IA Groq
                        reply = f"Salut ! Ir Chris AI a reçu : {text}"
                        send_message(sender, reply)
    return "OK", 200

def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": text}}
    requests.post(url, json=payload)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
