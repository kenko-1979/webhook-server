from flask import Flask, request
import requests
import os

app = Flask(__name__)

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")

@app.route("/webhook", methods=["POST"],strict_slashes=False)
def webhook():
    data = request.json
    content = data.get("message", "No message")

    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Title": {
                "title": [{"text": {"content": content}}]
            }
        }
    }

    res = requests.post("https://api.notion.com/v1/pages", json=payload, headers=headers)
    return {"status": "success", "notion_status": res.status_code}, res.status_code


