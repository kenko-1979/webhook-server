import requests
import os
from dotenv import load_dotenv

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
   

