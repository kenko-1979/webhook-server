import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# デバッグ用の出力を追加
print("Current working directory:", os.getcwd())
print("Environment variables check:")
print(f"NOTION_TOKEN exists: {'NOTION_TOKEN' in os.environ}")
print(f"NOTION_DATABASE_ID exists: {'NOTION_DATABASE_ID' in os.environ}")

def test_notion_connection():
    """Test Notion API connection and token validity"""
    NOTION_TOKEN = os.getenv('NOTION_TOKEN')
    NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
    
    if not NOTION_TOKEN or not NOTION_DATABASE_ID:
        print("Error: Missing environment variables")
        print(f"NOTION_TOKEN: {NOTION_TOKEN}")
        print(f"NOTION_DATABASE_ID: {NOTION_DATABASE_ID}")
        return False
    
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28"
    }
    
    # Test the connection by trying to retrieve the database
    try:
        response = requests.get(
            f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}",
            headers=headers
        )
        if response.status_code == 200:
            print("✅ Notion connection successful!")
            return True
        else:
            print(f"❌ Error: {response.status_code}")

            try:
                print(f"Response: {response.json()}")
            except Exception as json_err:
                print(f"⚠️ Could not parse JSON: {str(json_err)}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to Notion: {str(e)}")
        return False

# Test Notion connection first
if test_notion_connection():
    # Original webhook test code
    url = "http://localhost:10000/webhook"
    data = {"message": "テスト送信 from python"}
    
    res = requests.post(url, json=data)
    
   
    print("\n🚀 Webhook test results:")
    print(f"📨 Status code: {res.status_code}")
    print(f"📨 Response: {res.text}")
else:
    print("🛑 Please fix Notion connection issues before testing webhook")

def test_chat_endpoint(message, title, content, summary, is_production=False):
    """チャットエンドポイントをテストする"""
    # 本番環境のURLを使用するかローカルのURLを使用するか
    base_url = "https://webhook-server-c2h0.onrender.com" if is_production else "http://localhost:10000"
    url = f"{base_url}/chat"
    
    payload = {
        "message": message,
        "title": title,
        "content": content,
        "summary": summary
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"\n🚀 Testing endpoint: {url}")
        print(f"📦 Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        response = requests.post(url, json=payload, headers=headers)
        print(f"📡 Status Code: {response.status_code}")
        print(f"📬 Response: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    # 本番環境でテストを実行するかどうか
    IS_PRODUCTION = True  # Trueに設定すると本番環境、Falseでローカル環境
    
    print("=== Notion Webhook Server Test ===")
    print(f"🌍 Environment: {'Production' if IS_PRODUCTION else 'Local'}")
    
    # テストケース1: 保存トリガーあり
    test_chat_endpoint(
        message="要約送信",
        title="テスト会話1",
        content="これはテスト用の会話内容です。長い会話の全文がここに入ります。",
        summary="テスト用の会話のサマリーです。",
        is_production=IS_PRODUCTION
    )
    
    # テストケース2: 保存トリガーなし
    test_chat_endpoint(
        message="普通の会話",
        title="テスト会話2",
        content="これは保存されないはずの会話です。",
        summary="保存されないサマリー",
        is_production=IS_PRODUCTION
    )
   

