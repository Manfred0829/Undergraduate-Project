import json
import requests
import time
import subprocess
from flask import Flask, render_template, request, redirect, url_for
from pyngrok import ngrok  # 確保已安裝 pip install pyngrok
import config

PORT = 5002

# Rebrandly 設定（請填入你的 API Key 和 Domain）
REBRANDLY_API_KEY = config.get_env_variable("REBRANDLY_API_KEY")
REBRANDLY_LINK_ID = config.get_env_variable("REBRANDLY_LINK_ID")

ngrok.set_auth_token(config.get_env_variable("NFROK_AUTH_TOKEN"))

app = Flask(__name__)

@app.route('/')
def login_interface():
    return render_template('login_interface.html')

@app.route('/login', methods=['POST'])
def login():
    return redirect(url_for('user_interface'))

@app.route('/user_interface')
def user_interface():
    return render_template('user_interface.html')  # return render_template('user_interface.html')

def start_ngrok():
    """ 開啟 ngrok 隧道並取得公開網址 """
    public_url = ngrok.connect(PORT).public_url  # 建立 5000 端口的公開網址
    print(f"ngrok 隧道已啟動: {public_url}")
    return public_url

def update_rebrandly(new_url):
    """ 將 ngrok 的網址更新到 Rebrandly 短網址 """
    headers = {
        "Content-Type": "application/json",
        "apikey": REBRANDLY_API_KEY
    }

    data = {
        "destination": new_url
    }

    response = requests.post(
        f"https://api.rebrandly.com/v1/links/{REBRANDLY_LINK_ID}",
        headers=headers,
        data=json.dumps(data)
    )

    if response.status_code == 200:
        print("Rebrandly 短網址已連結至ngrok: https://rebrand.ly/JohnnyDo-flask-app")
    else:
        print(f"Rebrandly 更新失敗: {response.text}")

if __name__ == '__main__':
    # 1️⃣ 啟動 ngrok 並取得公開網址
    ngrok_url = start_ngrok()

    # 2️⃣ 更新 Rebrandly 短網址（僅執行一次）
    update_rebrandly(ngrok_url)

    # 3️⃣ 啟動 Flask 伺服器
    app.run(host='0.0.0.0', port=PORT, debug=False)
