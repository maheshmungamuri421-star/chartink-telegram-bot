from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ⚠️ ఇక్కడ మీ కొత్త టోకెన్ మరియు Chat ID పెట్టండి
TELEGRAM_BOT_TOKEN = "8803648646:AAHl1sBv3K-eHlcKMqc4OoDflx7Od6fa7uQ"
TELEGRAM_CHAT_ID = "7229600818"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

@app.route("/", methods=["GET"])
def home():
    return "Chartink Webhook is Running!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if not data:
        return {"status": "no data"}, 400

    # సీక్రెట్ చెక్ (కావాలంటే ఇక్కడ పెట్టుకోవచ్చు)
    # secret = request.args.get("secret")
    # if secret != "MySecret123":
    #     return {"status": "unauthorized"}, 403

    message = f"📊 Chartink Alert: {data.get('scan_name', 'N/A')}\n\n"
    message += f"⏰ Time: {data.get('triggered_at', 'N/A')}\n\n"
    message += f"📈 Stocks: {data.get('stocks', 'N/A')}\n"
    message += f"💰 Prices: {data.get('trigger_prices', 'N/A')}"

    send_telegram(message)
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
