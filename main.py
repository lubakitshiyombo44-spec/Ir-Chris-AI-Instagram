import os
import requests
import datetime
from flask import Flask, request

app = Flask(__name__)

CREATOR = "Ir Chris Lubaki Tshiyombo"
GROQ_KEY = os.getenv("GROQ_API_KEY", "").strip()
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "ir_chris_2026").strip()
PAGE_TOKEN = os.getenv("INSTA_PAGE_TOKEN", "").strip()

LOGS = []

def add_log(nom, heure, question, reponse):
    LOGS.insert(0, {"nom": nom, "heure": heure, "question": question, "reponse": reponse})
    if len(LOGS) > 200: LOGS.pop()

def get_instagram_name(user_id):
    if not PAGE_TOKEN: return f"User {user_id[:5]}"
    try:
        url = f"https://graph.facebook.com/v22.0/{user_id}?fields=name,username&access_token={PAGE_TOKEN}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            d = r.json()
            return d.get("name") or d.get("username") or f"User {user_id[:5]}"
    except: pass
    return f"User {user_id[:5]}"

def send_instagram_message(recipient_id, text):
    if not PAGE_TOKEN: return
    url = f"https://graph.facebook.com/v22.0/me/messages?access_token={PAGE_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": text[:1900]}}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def get_ai_response(question, first_name="ami"):
    ql = question.lower()
    if any(x in ql for x in ["qui t'a créé", "qui ta cree", "who made you", "who created you", "nani alikupa"]):
        return f"J'ai été créé par {CREATOR}."
    if ql in ["/start", "salut", "bonjour", "hello", "mbote", "jambo", "salam"]:
        return f"Mbote {first_name}! 👋 Je suis Ir Chris AI, créé par {CREATOR}. Je parle 6 langues : Français, English, Swahili, Lingala, Kiluba, Kisongye. Comment puis-je t'aider?"

    if not GROQ_KEY:
        return f"Désolé {first_name}, clé manquante."

    system_prompt = f"""Tu es Ir Chris AI, créé par {CREATOR}.
1. Créateur = {CREATOR}
2. Tu parles UNIQUEMENT 6 langues : Français, English, Swahili, Lingala, Kiluba, Kisongye. Si autre langue, dis : "Désolé {first_name}, je ne parle que 6 langues : Français, English, Swahili, Lingala, Kiluba, Kisongye."
3. Parle à l'utilisateur par son prénom : {first_name}
4. Pas d'hallucination."""

    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
            json={"model": "openai/gpt-oss-20b", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": question}], "temperature": 0.5, "max_tokens": 800},
            timeout=30)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
        return f"Désolé {first_name}, petite panne. Réessaie."
    except:
        return f"Désolé {first_name}, connexion lente."

@app.route("/")
def home():
    return f"Ir Chris AI Instagram Actif - Par {CREATOR} - <a href='/admin'>ADMIN</a>"

@app.route("/admin")
def admin_panel():
    rows = ""
    for log in LOGS:
        rows += f"<tr><td style='color:#38bdf8;font-weight:bold'>{log['nom']}</td><td>{log['heure']}</td><td>{log['question']}</td><td style='color:#22c55e'>{log['reponse'][:1000]}</td></tr>"
    if not rows:
        rows = "<tr><td colspan=4 style='text-align:center;padding:30px'>Aucun DM encore</td></tr>"
    return f"<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'><style>body{{background:#0f172a;color:white;font-family:Arial;padding:15px}} table{{width:100%;background:#1e293b;border-collapse:collapse;border-radius:12px;overflow:hidden}} th{{background:#334155;padding:12px;text-align:left}} td{{padding:10px;border-bottom:1px solid #334155;vertical-align:top;font-size:14px}}</style></head><body><h1>📩 Panneau Admin Instagram - Ir Chris AI</h1><p>Créé par {CREATOR} | Total: {len(LOGS)}</p><table><tr><th>👤 Nom de la personne</th><th>🕒 Heure</th><th>💬 Question posée</th><th>🤖 Réponse de mon IA</th></tr>{rows}</table></body></html>"

@app.route("/webhook/instagram", methods=["GET"])
def verify_webhook():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Forbidden", 403

@app.route("/webhook/instagram", methods=["POST"])
def receive_message():
    body = request.get_json(force=True) or {}
    try:
        for entry in body.get("entry", []):
            for messaging in entry.get("messaging", []):
                if "message" in messaging and "text" in messaging["message"]:
                    question = messaging["message"]["text"].strip()
                    sender_id = messaging["sender"]["id"]
                    full_name = get_instagram_name(sender_id)
                    first_name = full_name.split()[0]
                    heure = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    reponse = get_ai_response(question, first_name)
                    add_log(full_name, heure, question, reponse)
                    send_instagram_message(sender_id, reponse)
    except Exception as e:
        print(e)
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
