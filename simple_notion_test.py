import os
from dotenv import load_dotenv
import requests
import json

# 環境変数の読み込み
load_dotenv()

NOTION_TOKEN = os.getenv('NOTION_TOKEN')
# データベースIDにハイフンを追加
original_db_id = os.getenv('NOTION_DATABASE_ID')
NOTION_DATABASE_ID = f"{original_db_id[:8]}-{original_db_id[8:12]}-{original_db_id[12:16]}-{original_db_id[16:20]}-{original_db_id[20:]}"

# ヘッダーの設定（APIバージョンを最新に更新）
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

print("=== Notion API テスト ===")
print(f"元のデータベースID: {original_db_id}")
print(f"変換後のデータベースID: {NOTION_DATABASE_ID}")
print(f"トークンの存在: {'はい' if NOTION_TOKEN else 'いいえ'}")

# まずデータベースの情報を取得してみる
print("\n=== データベース情報の取得 ===")
database_url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}"
try:
    database_response = requests.get(database_url, headers=headers)
    print(f"データベース取得ステータスコード: {database_response.status_code}")
    print("データベースのレスポンス:")
    print(json.dumps(database_response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"データベース取得でエラー: {str(e)}")

# ページ作成のテスト
print("\n=== ページ作成テスト ===")
create_page_url = "https://api.notion.com/v1/pages"
data = {
    "parent": { "database_id": NOTION_DATABASE_ID },
    "properties": {
        "名前": {
            "title": [
                {
                    "text": {
                        "content": "APIテスト投稿"
                    }
                }
            ]
        }
    }
}

try:
    response = requests.post(create_page_url, headers=headers, json=data)
    print(f"ページ作成ステータスコード: {response.status_code}")
    print("レスポンス内容:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"\nエラーが発生しました: {str(e)}") 