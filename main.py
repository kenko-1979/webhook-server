from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from notion_client import Client
import os
from dotenv import load_dotenv
import requests
from datetime import datetime
import json

# 常に.envを読み込む（開発環境でもプロダクション環境でも）
load_dotenv()

app = FastAPI()
notion = Client(auth=os.environ["NOTION_API_KEY"])

# 環境変数の取得
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID").strip() if os.getenv("NOTION_DATABASE_ID") else None
IS_PRODUCTION = os.getenv('FLASK_ENV') == 'production'

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

def create_notion_page(title, summary, content):
    """Notionページを作成する"""
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    # 要約とコンテンツを結合
    combined_text = f"要約:\n{summary}\n\n内容:\n{content}"

    # 現在の日時を日本時間で取得（時分秒まで表示）
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "名前": {
                "id": "title",
                "type": "title",
                "title": [{"text": {"content": title}}]
            },
            "テキスト": {
                "rich_text": [{"text": {"content": combined_text}}]
            },
            "日付": {
                "date": {
                    "start": current_time
                }
            },
            "URL": {
                "rich_text": [{"text": {"content": "https://chat.openai.com"}}]
            }
        }
    }

    try:
        res = requests.post(
            "https://api.notion.com/v1/pages",
            headers=headers,
            json=payload
        )
        
        if res.status_code in [200, 201]:
            return True, res.json()
        else:
            error_msg = res.json().get('message', f'Notion API error: {res.status_code}')
            safe_log("❌ Notionエラーの詳細", {"error": error_msg, "response": res.json()})
            return False, error_msg
    except Exception as e:
        return False, str(e)

@app.post("/webhook")
async def handle_webhook(request: Request):
    try:
        body = await request.json()
        
        # Notionのwebhook認証チャレンジに応答
        if body.get("type") == "url_verification":
            challenge = body.get("challenge")
            safe_log("📝 Webhook認証チャレンジを受信", {"challenge": challenge})
            return JSONResponse({"type": "url_verification", "challenge": challenge})
        
        # 通常のwebhookリクエストの処理
        safe_log("📥 Webhookリクエストを受信", {"body": body})
        
        # 既存のNotion処理ロジック
        database_id = os.environ["NOTION_DATABASE_ID"]
        # データベース処理ロジック
        return JSONResponse({"status": "success"})
    except Exception as e:
        safe_log("❌ Webhookエラー", {"error": str(e)})
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/")
async def root():
    return {"message": "Notion Webhook Server is running"}

# Vercel用のWSGIアプリケーション
app = app

if __name__ == "__main__":
    if not NOTION_TOKEN or not NOTION_DATABASE_ID:
        print("❌ 環境変数（NOTION_TOKENまたはDATABASE_ID）が未設定です")
    elif not test_notion_connection():
        print("❌ Notionの接続テストに失敗しました。トークンまたはDatabase IDを確認してください。")
    else:
        safe_log("✅ Notion接続テスト成功")
        port = int(os.getenv("PORT", 10000))
        safe_log(f"🚀 サーバーを起動します（ポート: {port}）")
        app.run(host="0.0.0.0", port=port)
