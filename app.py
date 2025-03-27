import json
import requests
import time
import subprocess
from flask import Flask, render_template, request, redirect, url_for
from pyngrok import ngrok  # 確保已安裝 pip install pyngrok

# Rebrandly 設定（請填入你的 API Key 和 Domain）
REBRANDLY_API_KEY = "000289fd396d44248b70567e2ac9dab4"
REBRANDLY_LINK_ID = "07c4e1aefb354771a5c4be8904ac0dae"  # 例如 "xyz123" (從 Rebrandly 網址設定中取得)

ngrok.set_auth_token("2tfriendjn7OPP98aWS1j2mBrCN_2vNRGFCwj4ATujaFik4xC")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    return redirect(url_for('main'))

@app.route('/main')
def main():
    return render_template('main.html')

def start_ngrok():
    """ 開啟 ngrok 隧道並取得公開網址 """
    public_url = ngrok.connect(5000).public_url  # 建立 5000 端口的公開網址
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
        print(f"Rebrandly 短網址已更新至: {new_url}")
    else:
        print(f"Rebrandly 更新失敗: {response.text}")

if __name__ == '__main__':
    # 1️⃣ 啟動 ngrok 並取得公開網址
    ngrok_url = start_ngrok()

    # 2️⃣ 更新 Rebrandly 短網址（僅執行一次）
    update_rebrandly(ngrok_url)

    # 3️⃣ 啟動 Flask 伺服器
    app.run(host='0.0.0.0', port=5000, debug=False)
