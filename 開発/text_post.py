import requests

url = "https://webhook-server-c2h0.onrender.com/webhook"  # ← Render のURLに変更
data = {"message": "Render 経由のテスト送信"}

res = requests.post(url, json=data)

print("ステータスコード:", res.status_code)
print("レスポンス本文:", res.text)

