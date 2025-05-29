import os
from dotenv import load_dotenv

# .envファイルを読み込む
print("Loading .env file...")
load_dotenv()

# 環境変数の値を確認
print("\nEnvironment variables:")
print(f"NOTION_TOKEN: {'*' * len(os.getenv('NOTION_TOKEN', ''))} (length: {len(os.getenv('NOTION_TOKEN', ''))})")
print(f"NOTION_DATABASE_ID: {os.getenv('NOTION_DATABASE_ID')}")
print(f"FLASK_ENV: {os.getenv('FLASK_ENV')}")

# データベースIDの詳細を確認
db_id = os.getenv('NOTION_DATABASE_ID')
if db_id:
    print(f"\nDatabase ID details:")
    print(f"Length: {len(db_id)}")
    print(f"Contains hyphens: {'-' in db_id}")
    print(f"Contains spaces: {' ' in db_id}")
    print(f"Raw bytes: {db_id.encode()}") 