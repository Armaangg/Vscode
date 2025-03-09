import requests
import time
import pytz
from datetime import datetime
from flask import Flask

app = Flask(__name__)

WEBHOOK_URL = 'https://discord.com/api/webhooks/1348251353176211466/aJuTBKtxqOUCbHqOTamKZsuP4EmWDofZqq9o9FFZvbyuczL5JwhZHmBcAIc4SKKA9Z3b'
MESSAGE_ID = '1348286214284906618'
API_URL = 'http://fi1.bot-hosting.net:6957/'

uptime = 0
downtime = 0

def edit_message(embed):
    response = requests.patch(f"{WEBHOOK_URL}/messages/{MESSAGE_ID}", json={"embeds": [embed]})
    return response

def build_embed(status):
    now = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %I:%M:%S %p')
    color = 0x00FF00 if status == 'Online' else 0xFF0000
    return {
        "title": "API STATUS",
        "color": color,
        "fields": [
            {"name": "Uptime", "value": f"{uptime} seconds", "inline": True},
            {"name": "Downtime", "value": f"{downtime} seconds", "inline": True},
            {"name": "Status", "value": status, "inline": True},
            {"name": "Last Updated", "value": now, "inline": False}
        ]
    }

@app.route("/")
def home():
    global uptime, downtime
    previous_status = None

    while True:
        try:
            response = requests.get(API_URL)
            if response.status_code == 200:
                if previous_status != 'Online':
                    embed = build_embed('Online')
                    edit_message(embed)
                previous_status = 'Online'
                uptime += 1
            else:
                if previous_status != 'Offline':
                    embed = build_embed('Offline')
                    edit_message(embed)
                previous_status = 'Offline'
                downtime += 1
        except:
            if previous_status != 'Offline':
                embed = build_embed('Offline')
                edit_message(embed)
            previous_status = 'Offline'
            downtime += 1
        
        time.sleep(1)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
