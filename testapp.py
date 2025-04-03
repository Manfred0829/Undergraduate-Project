import json
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for
from pyngrok import ngrok  # 確保已安裝 pip install pyngrok

PORT = 5002

# Rebrandly 設定（請填入你的 API Key 和 Domain）
REBRANDLY_API_KEY = "000289fd396d44248b70567e2ac9dab4"
REBRANDLY_LINK_ID = "07c4e1aefb354771a5c4be8904ac0dae"

ngrok.set_auth_token("2tfriendjn7OPP98aWS1j2mBrCN_2vNRGFCwj4ATujaFik4xC")

app = Flask(__name__)

# 模擬的動態數據
status_data = {"message": "伺服器已啟動", "count": 0}

@app.route('/')
def login_interface():
    return render_template('login_interface.html')

@app.route('/login', methods=['POST'])
def login():
    return redirect(url_for('user_interface'))

@app.route('/user_interface')
def user_interface():
    return render_template('user_interface.html')

@app.route('/status', methods=['GET'])
def get_status():
    """提供前端可查詢的伺服器狀態 API"""
    global status_data
    status_data["count"] += 1  # 每次請求時增加計數
    return jsonify(status_data)

def start_ngrok():
    """開啟 ngrok 隧道並取得公開網址"""
    public_url = ngrok.connect(PORT).public_url  # 建立 5002 端口的公開網址
    print(f"ngrok 隧道已啟動: {public_url}")
    return public_url

def update_rebrandly(new_url):
    """將 ngrok 的網址更新到 Rebrandly 短網址"""
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
    # 啟動 ngrok 並取得公開網址
    ngrok_url = start_ngrok()

    # 更新 Rebrandly 短網址（僅執行一次）
    update_rebrandly(ngrok_url)

    # 啟動 Flask 伺服器
    app.run(host='0.0.0.0', port=PORT, debug=False)