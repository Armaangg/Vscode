import requests
import json
import time
from datetime import datetime

# Discord Webhook URL
webhook_url = "https://discord.com/api/webhooks/1348251353176211466/aJuTBKtxqOUCbHqOTamKZsuP4EmWDofZqq9o9FFZvbyuczL5JwhZHmBcAIc4SKKA9Z3b"

# File to store data
data_file = "status_data.json"

# Load existing data or set defaults
try:
    with open(data_file, "r") as file:
        data = json.load(file)
except FileNotFoundError:
    data = {
        "message_id": None,
        "uptime": 0,
        "downtime": 0,
        "last_status": None
    }

# Function to send a Discord message
def send_message(content):
    response = requests.post(webhook_url, json=content)
    return response.json()

# Function to edit a Discord message
def edit_message(message_id, content):
    url = f"{webhook_url}/messages/{message_id}"
    requests.patch(url, json=content)

# Infinite loop to check API status every second
while True:
    try:
        # Check API status
        response = requests.get("http://fi1.bot-hosting.net:6957/", timeout=5)
        is_online = response.status_code == 200
    except requests.RequestException:
        is_online = False

    # Update uptime/downtime
    if is_online:
        data["uptime"] += 1
        color = 3066993  # Green
        status_text = "🟢 Online"
    else:
        data["downtime"] += 1
        color = 15158332  # Red
        status_text = "🔴 Offline"

    # Current timestamp
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create embed content
    embed = {
        "embeds": [{
            "title": "API Status",
            "color": color,
            "fields": [
                {"name": "Uptime", "value": f"{data['uptime']} seconds", "inline": True},
                {"name": "Downtime", "value": f"{data['downtime']} seconds", "inline": True},
                {"name": "Status", "value": status_text, "inline": True},
                {"name": "Last Updated", "value": last_updated, "inline": False}
            ]
        }]
    }

    # Send or edit message
    if data["message_id"] is None:
        response = send_message(embed)
        if "id" in response:
            data["message_id"] = response["id"]
    else:
        edit_message(data["message_id"], embed)

    # Save data to file
    with open(data_file, "w") as file:
        json.dump(data, file)

    # Wait 1 second before checking again
    time.sleep(1)
