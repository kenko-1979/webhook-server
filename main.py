from flask import Flask, request
import os
import requests
from dotenv import load_dotenv
import json

# 開発環境でのみ.envを読み込む
if os.getenv('FLASK_ENV') != 'production':
    load_dotenv()

app = Flask(__name__)

# 環境変数の取得
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
original_db_id = os.getenv("NOTION_DATABASE_ID")
IS_PRODUCTION = os.getenv('FLASK_ENV') == 'production'

# データベースIDにハイフンを追加
NOTION_DATABASE_ID = f"{original_db_id[:8]}-{original_db_id[8:12]}-{original_db_id[12:16]}-{original_db_id[16:20]}-{original_db_id[20:]}"

def safe_log(message, data=None):
    """本番環境ではセンシティブな情報をログ出力しない"""
    if IS_PRODUCTION:
        if isinstance(data, dict):
            # センシティブな情報を除去
            safe_data = data.copy()
            if 'notion_response' in safe_data:
                safe_data['notion_response'] = '[REDACTED]'
            print(f"{message}: {json.dumps(safe_data, ensure_ascii=False)}")
        else:
            print(message)
    else:
        if data:
            print(f"{message}: {json.dumps(data, ensure_ascii=False)}")
        else:
            print(message)

def test_notion_connection():
    """トークンとデータベースIDの正当性を確認"""
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    res = requests.get(
        f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}",
        headers=headers
    )
    return res.status_code == 200

@app.route("/webhook", methods=["POST"])
def webhook():
    if not request.is_json:
        return {"error": "Content-Type must be application/json"}, 415

    try:
        data = request.get_json()
        if data is None:
            return {"error": "Invalid JSON"}, 400
    except Exception as e:
        return {"error": f"JSON parse error: {str(e)}"}, 400

    content = data.get("message", "No message")
    safe_log("📥 受信内容", {"message": content})

    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "名前": {
                "title": [{"text": {"content": content}}]
            },
            "Status": {
                "status": {
                    "name": "未着手"
                }
            },
            "テキスト": {
                "rich_text": [{"text": {"content": "Webhookから自動作成されました"}}]
            }
        }
    }

    res = requests.post("https://api.notion.com/v1/pages", json=payload, headers=headers)
    
    safe_log("📤 Notionレスポンス", {
        "status_code": res.status_code,
        "notion_response": res.text
    })
    
    return {
        "status": "success" if res.status_code in [200, 201] else "error",
        "notion_status": res.status_code,
        "notion_response": "[REDACTED]" if IS_PRODUCTION else res.text
    }, 200 if res.status_code in [200, 201] else 500

if __name__ == "__main__":
    if not NOTION_TOKEN or not original_db_id:
        print("❌ 環境変数（NOTION_TOKENまたはDATABASE_ID）が未設定です")
    elif not test_notion_connection():
        print("❌ Notionの接続テストに失敗しました。トークンまたはDatabase IDを確認してください。")
    else:
        safe_log("✅ Notion接続テスト成功")
        port = int(os.getenv("PORT", 10000))
        safe_log(f"🚀 サーバーを起動します（ポート: {port}）")
        app.run(host="0.0.0.0", port=port)
