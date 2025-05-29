from flask import Flask, request
import os
import requests
from dotenv import load_dotenv
import json
import hmac
import hashlib

# 常に.envを読み込む（開発環境でもプロダクション環境でも）
load_dotenv()

app = Flask(__name__)

# 環境変数の取得
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
original_db_id = os.getenv("NOTION_DATABASE_ID")
IS_PRODUCTION = os.getenv('FLASK_ENV') == 'production'

# Webhookの検証トークンを保存するグローバル変数
WEBHOOK_SECRET = None

# デバッグ用：環境変数の値を確認
print(f"Original Database ID: {original_db_id}")
print(f"FLASK_ENV: {os.getenv('FLASK_ENV')}")
print(f"IS_PRODUCTION: {IS_PRODUCTION}")

# データベースIDをそのまま使用（ハイフンの処理を行わない）
NOTION_DATABASE_ID = original_db_id.strip() if original_db_id else None
print(f"Using Database ID: {NOTION_DATABASE_ID}")

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
    try:
        res = requests.get(
            f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}",
            headers=headers
        )
        safe_log("Notion接続テストレスポンス", {
            "status_code": res.status_code,
            "response": res.text if not IS_PRODUCTION else "[REDACTED]"
        })
        return res.status_code in [200, 201]
    except Exception as e:
        safe_log(f"Notion接続テストでエラー: {str(e)}")
        return False

def verify_notion_request(request_body, signature_header):
    """Notionからのリクエストを検証する"""
    if not WEBHOOK_SECRET:
        return True  # 検証トークンがない場合は検証をスキップ
    
    try:
        signature = f"sha256={hmac.new(WEBHOOK_SECRET.encode(), request_body, hashlib.sha256).hexdigest()}"
        return hmac.compare_digest(signature, signature_header)
    except Exception as e:
        safe_log(f"署名検証エラー: {str(e)}")
        return False

@app.route("/test", methods=["GET"])
def test():
    return {"status": "ok"}, 200

@app.route("/", methods=["GET"])
def index():
    return {"status": "Webhook Server is running"}, 200

@app.route("/webhook", methods=["POST"])
def webhook():
    global WEBHOOK_SECRET
    
    # リクエストのContent-Typeチェック
    if not request.is_json:
        return {"error": "Content-Type must be application/json"}, 415

    try:
        # リクエストボディを取得
        request_body = request.get_data()
        data = request.get_json()
        
        # Webhookの検証
        if 'verification_token' in data:
            # 初期検証リクエストの処理
            WEBHOOK_SECRET = data['verification_token']
            safe_log("Webhook検証トークンを受信しました")
            safe_log(f"受信したトークン: {WEBHOOK_SECRET}")
            return {"status": "success"}, 200
            
        # 通常のWebhookリクエストの処理
        signature_header = request.headers.get('x-notion-signature')
        if signature_header and not verify_notion_request(request_body, signature_header):
            return {"error": "Invalid signature"}, 401

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
        print(f"[DEBUG] Request payload: {json.dumps(payload, ensure_ascii=False)}")

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

    except Exception as e:
        safe_log(f"Webhookエラー: {str(e)}")
        return {"error": str(e)}, 500

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
