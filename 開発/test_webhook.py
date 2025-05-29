import requests
import json

def test_webhook():
    url = 'http://localhost:10000/webhook'
    headers = {'Content-Type': 'application/json'}
    data = {'message': 'Pythonスクリプトからのテスト送信'}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_webhook() 