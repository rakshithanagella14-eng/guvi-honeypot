
from flask import Flask, request, jsonify
import re
import requests

app = Flask(__name__)


SCAM_WORDS = [
    "urgent", "account blocked", "verify now", "suspended", "fraud", "security alert",
    "act fast", "limited time", "bank issue", "payment due", "reward pending", "click here",
    "win prize", "lottery", "inheritance", "job offer", "refund", "tax refund", "virus detected",
    "otp", "password", "login", "transfer", "money"
]

API_KEY = "mykey123"  

@app.route('/honeypot', methods=['POST'])
def honeypot():
    
    if request.headers.get('x-api-key') != API_KEY:
        return jsonify({"error": "Wrong password!"}), 401
    
    
    data = request.json
    session_id = data['sessionId']
    message_text = data['message']['text']
    history = data.get('conversationHistory', [])
    
    
    is_scam = any(word in message_text.lower() for word in SCAM_WORDS)
    
    if not is_scam:
        return jsonify({"status": "success", "reply": "I don't understand what you mean."})
    
    
    if "account" in message_text.lower() or "blocked" in message_text.lower():
        reply = "Oh no! Why is my account blocked? I'm really worried—please help!"
    elif "upi" in message_text.lower() or "id" in message_text.lower():
        reply = "Okay, my UPI ID is victim@fakebank. What should I do next?"
    elif "link" in message_text.lower() or "click" in message_text.lower():
        reply = "Is this link safe? Let me check it out."
    elif "phone" in message_text.lower() or "otp" in message_text.lower():
        reply = "I sent the OTP! My phone number is 9876543210."
    elif "money" in message_text.lower() or "payment" in message_text.lower():
        reply = "How much do I need to pay? I'm ready."
    elif "password" in message_text.lower() or "login" in message_text.lower():
        reply = "My password is secret123. Is that enough?"
    else:
        reply = "I'm scared! Can you tell me more details?"
    
    
    upi_ids = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', message_text)
    bank_accounts = re.findall(r'\b\d{4,16}\b', message_text)  
    phishing_links = re.findall(r'http[s]?://[^\s]+', message_text)
    phone_numbers = re.findall(r'\b\d{10}\b', message_text)
    suspicious_keywords = [word for word in SCAM_WORDS if word in message_text.lower()]
    
    intelligence = {
        "bankAccounts": bank_accounts,
        "upiIds": upi_ids,
        "phishingLinks": phishing_links,
        "phoneNumbers": phone_numbers,
        "suspiciousKeywords": suspicious_keywords
    }
    
    
    if len(history) > 6:
        payload = {
            "sessionId": session_id,
            "scamDetected": True,
            "totalMessagesExchanged": len(history) + 1,
            "extractedIntelligence": intelligence,
            "agentNotes": "Detected scam with keywords, engaged interactively, extracted UPI, links, and more."
        }
        try:
            requests.post("https://hackathon.guvi.in/api/updateHoneyPotFinalResult", json=payload, timeout=5)
        except:
            pass  
    
    return jsonify({"status": "success", "reply": reply})

if __name__ == '__main__':
    app.run(debug=True)