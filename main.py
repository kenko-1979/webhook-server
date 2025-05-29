from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv
import json
from datetime import datetime

# 常に.envを読み込む（開発環境でもプロダクション環境でも）
load_dotenv()

app = Flask(__name__)

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
                    "start": datetime.now().isoformat()
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

@app.route("/", methods=["GET"])
def index():
    return {"status": "Server is running"}, 200

@app.route("/chat", methods=["POST"])
def handle_chat():
    """チャット内容を受け取り、必要に応じてNotionに保存する"""
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

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
        safe_log("📥 Notionへの保存を開始", {
            "title": title,
            "summary_length": len(summary),
            "content_length": len(content)
        })
        
        success, result = create_notion_page(title, summary, content)
        
        if success:
            safe_log("✅ Notionへの保存が完了", {
                "page_id": result.get("id")
            })
            return jsonify({
                "status": "success",
                "message": "Notionに保存しました",
                "page_id": result.get("id")
            })
        else:
            safe_log("❌ Notionへの保存に失敗", {
                "error": result
            })
            return jsonify({
                "status": "error",
                "message": f"Notionへの保存に失敗しました: {result}"
            }), 500
    else:
        return jsonify({
            "status": "ignored",
            "message": "保存トリガーが検出されませんでした"
        })

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
