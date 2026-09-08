from flask import Flask, request
import os

app = Flask(__name__)

VERIFY_TOKEN = "Chris2026"

@app.route('/')
def home():
    return "Bot Ir Chris AI OK", 200

@app.route('/webhook', methods=['GET'])
def verify():
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if token == VERIFY_TOKEN:
        return challenge, 200
    return "Token invalide", 403

@app.route('/webhook', methods=['POST'])
def incoming():
    print(request.get_json())
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
