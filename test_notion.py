import os
from dotenv import load_dotenv
import requests
import json

# 開発環境の.envを読み込む
load_dotenv()

def test_notion_api():
    # 環境変数の取得と表示
    token = os.getenv("NOTION_TOKEN")
    db_id = os.getenv("NOTION_DATABASE_ID")
    print(f"Database ID: {db_id}")
    
    # APIヘッダーの設定
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # データベース情報の取得
    print("\n1. データベース情報の取得:")
    try:
        res = requests.get(
            f"https://api.notion.com/v1/databases/{db_id}",
            headers=headers
        )
        print(f"Status: {res.status_code}")
        print(f"Response: {json.dumps(res.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # テストページの作成
    print("\n2. テストページの作成:")
    try:
        payload = {
            "parent": {"database_id": db_id},
            "properties": {
                "名前": {
                    "title": [{"text": {"content": "APIテスト投稿"}}]
                },
                "Status": {
                    "status": {
                        "name": "未着手"
                    }
                },
                "テキスト": {
                    "rich_text": [{"text": {"content": "APIテストからの投稿です"}}]
                }
            }
        }
        res = requests.post(
            "https://api.notion.com/v1/pages",
            headers=headers,
            json=payload
        )
        print(f"Status: {res.status_code}")
        print(f"Response: {json.dumps(res.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_notion_api() 