import os
from dotenv import load_dotenv
import requests
import json

# 環境変数の読み込み
load_dotenv()

# 本番環境のWebhook URL
WEBHOOK_URL = "https://webhook-server-c2h0.onrender.com/webhook"

print("=== Webhook テスト ===")

# Webhookへのテストリクエスト
test_data = {
    "message": "要約送信",
    "title": "会話タイトル",
    "content": "会話の全文",
    "summary": "会話の要約"
}

try:
    response = requests.post(WEBHOOK_URL, json=test_data)
    print(f"ステータスコード: {response.status_code}")
    print("レスポンス内容:")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        print(f"Raw response: {response.text}")
except Exception as e:
    print(f"\nエラーが発生しました: {str(e)}") 