from flask import Flask, request
import requests
import datetime
import pytz
import sqlite3
import os

app = Flask(__name__)

# ⚠️ ఇక్కడ మీ టెలిగ్రామ్ వివరాలు మార్చండి
BOT_TOKEN = "9293749369:AAHjk3Gtcpxvq6CgAPhTlb18vxj5yZNA28Q"
CHAT_ID = "7229600818"

# డేటాబేస్ సెటప్ (అలర్ట్స్ సేవ్ చేసుకోవడానికి)
def init_db():
    conn = sqlite3.connect('alerts.db')
    c = conn.cursor()
    # టేబుల్ క్రియేట్ చేయడం (స్టాక్ పేరు మరియు వారం నంబర్ సేవ్ అవుతుంది)
    c.execute('''CREATE TABLE IF NOT EXISTS sent_alerts
                 (stock_name TEXT, week_number INTEGER)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        if not data:
            return "No data", 400

        # ప్రస్తుత సమయం మరియు ఈ వారం నంబర్ తీసుకోవడం
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.datetime.now(ist)
        current_time = now.strftime("%I:%M %p")
        current_week = now.isocalendar()[1] # ఈ వారం నంబర్ (1-52)

        scan_name = data.get("scan_name", "Weekly Alert")
        stocks_str = data.get("stocks", "")
        prices_str = data.get("trigger_prices", "N/A")

        if not stocks_str:
            return "No stocks in data", 200

        # స్టాక్స్ లిస్ట్ ని విడదీయడం
        stocks_list = [s.strip() for s in stocks_str.split(',')]
        prices_list = [p.strip() for p in prices_str.split(',')]

        new_stocks = []
        new_prices = []

        # డేటాబేస్ ఓపెన్ చేయడం
        conn = sqlite3.connect('alerts.db')
        c = conn.cursor()

        for i, stock in enumerate(stocks_list):
            # ఈ వారం ఈ స్టాక్ అలర్ట్ ఇప్పటికే పంపారా అని చెక్ చేయడం
            c.execute("SELECT * FROM sent_alerts WHERE stock_name=? AND week_number=?", (stock, current_week))
            result = c.fetchone()

            if result is None:
                # అలర్ట్ పంపకపోతే, లిస్ట్ లో యాడ్ చేసి, డేటాబేస్ లో సేవ్ చేయడం
                new_stocks.append(stock)
                if i < len(prices_list):
                    new_prices.append(prices_list[i])
                
                c.execute("INSERT INTO sent_alerts (stock_name, week_number) VALUES (?, ?)", (stock, current_week))

        conn.commit()
        conn.close()

        # ఒకవేళ కొత్త స్టాక్స్ ఉంటేనే టెలిగ్రామ్ కి మెసేజ్ పంపడం
        if new_stocks:
            final_stocks = ", ".join(new_stocks)
            final_prices = ", ".join(new_prices) if new_prices else "N/A"

            message = f"""
📊 <b>Chartink Alert: {scan_name}</b>

⏰ <b>Time:</b> {current_time}

📈 <b>Stocks:</b> {final_stocks}
💰 <b>Prices:</b> {final_prices}
"""
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
            requests.post(url, json=payload)
            
            return f"Sent: {final_stocks}", 200
        else:
            # కొత్త స్టాక్స్ లేకపోతే మెసేజ్ పంపము (డూప్లికేట్ అలర్ట్స్ ఆగిపోతాయి)
            return "No new stocks this week", 200

    except Exception as e:
        print(f"Error: {e}")
        return "Error", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
