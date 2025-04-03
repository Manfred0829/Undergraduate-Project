import json
import requests
from config import Config

def update_rebrandly(new_url):
    headers = {
        "Content-Type": "application/json",
        "apikey": Config.REBRANDLY_API_KEY
    }

    data = {
        "destination": new_url
    }

    response = requests.post(
        f"https://api.rebrandly.com/v1/links/{Config.REBRANDLY_LINK_ID}",
        headers=headers,
        data=json.dumps(data)
    )

    if response.status_code == 200:
        print("Rebrandly 短網址已連結至ngrok: https://rebrand.ly/JohnnyDo-flask-app")
    else:
        print(f"Rebrandly 更新失敗: {response.text}") 