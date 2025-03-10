import requests
import time
import pytz
from datetime import datetime, timedelta
from flask import Flask
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

app = Flask(__name__)

WEBHOOK_URL = 'https://discord.com/api/webhooks/1348251353176211466/aJuTBKtxqOUCbHqOTamKZsuP4EmWDofZqq9o9FFZvbyuczL5JwhZHmBcAIc4SKKA9Z3b'
MESSAGE_ID = '1348286214284906618'
API_URL = 'http://fi1.bot-hosting.net:6957/'

uptime = timedelta()
downtime = timedelta()
last_check = datetime.now()

def format_time(delta):
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"

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
            {"name": "Uptime", "value": format_time(uptime), "inline": True},
            {"name": "Downtime", "value": format_time(downtime), "inline": True},
            {"name": "Status", "value": status, "inline": True},
            {"name": "Last Updated (ASIA/KOLKATA)", "value": now, "inline": False}
        ]
    }

def monitor_api():
    global uptime, downtime, last_check
    previous_status = None

    while True:
        now = datetime.now()
        elapsed = now - last_check
        last_check = now

        try:
            response = requests.get(API_URL)
            if response.status_code == 200:
                uptime += elapsed
                if previous_status != 'Online':
                    embed = build_embed('Online')
                    edit_message(embed)
                previous_status = 'Online'
            else:
                downtime += elapsed
                if previous_status != 'Offline':
                    embed = build_embed('Offline')
                    edit_message(embed)
                previous_status = 'Offline'
        except:
            downtime += elapsed
            if previous_status != 'Offline':
                embed = build_embed('Offline')
                edit_message(embed)
            previous_status = 'Offline'
        
        time.sleep(1)

@app.route("/")
def home():
    return "API Uptime Monitor Running"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

def run_http_server():
    class MyHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.path = '/index.html'
            return super().do_GET()

    server_address = ('', 8000)
    httpd = HTTPServer(server_address, MyHandler)
    print("Server running at http://localhost:8000")
    httpd.serve_forever()

# Run the API monitor in a separate thread
threading.Thread(target=monitor_api, daemon=True).start()

# Run Flask and HTTP server concurrently
threading.Thread(target=run_flask, daemon=True).start()
run_http_server()
