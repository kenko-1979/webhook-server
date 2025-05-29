from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv
import json
import hmac
import hashlib
from datetime import datetime
from notion_client import Client

# 常に.envを読み込む（開発環境でもプロダクション環境でも）
load_dotenv()

app = Flask(__name__)
notion = Client(auth=os.getenv("NOTION_TOKEN"))
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# 環境変数の取得
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
original_db_id = os.getenv("NOTION_DATABASE_ID")
IS_PRODUCTION = os.getenv('FLASK_ENV') == 'production'

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

def create_notion_page(title, summary, full_text):
    """Notionにページを作成する"""
    try:
        new_page = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Title": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                },
                "Date": {
                    "date": {
                        "start": datetime.now().date().isoformat()
                    }
                },
                "Summary": {
                    "rich_text": [
                        {
                            "text": {
                                "content": summary
                            }
                        }
                    ]
                },
                "Status": {
                    "select": {
                        "name": "Done"
                    }
                }
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": full_text
                                }
                            }
                        ]
                    }
                }
            ]
        )
        return True, new_page
    except Exception as e:
        return False, str(e)

@app.route("/chat", methods=["POST"])
def handle_chat():
    """チャット内容を受け取り、必要に応じてNotionに保存する"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    message = data.get("message", "").lower()
    title = data.get("title", "無題の会話")
    content = data.get("content", "")
    summary = data.get("summary", "")

    # 自然言語トリガーの判定
    save_triggers = ["要約送信", "notion送信", "保存", "送って", "notionに送って"]
    should_save = any(trigger in message for trigger in save_triggers)

    if should_save:
        success, result = create_notion_page(title, summary, content)
        if success:
            return jsonify({
                "status": "success",
                "message": "Notionに保存しました",
                "page_id": result["id"]
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Notionへの保存に失敗しました: {result}"
            }), 500
    else:
        return jsonify({
            "status": "ignored",
            "message": "保存トリガーが検出されませんでした"
        })

@app.route("/test", methods=["GET"])
def test():
    return {"status": "ok"}, 200

@app.route("/", methods=["GET"])
def index():
    """サーバーの状態を確認するエンドポイント"""
    return jsonify({
        "status": "running",
        "message": "サーバーは正常に動作しています"
    })

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
