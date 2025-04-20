from app import create_app
from app.services.ngrok_service import start_ngrok
from app.services.rebrandly_service import update_rebrandly

PORT = 5002
app = create_app()

if __name__ == '__main__':

    # 1️⃣ 啟動 ngrok 並取得公開網址
    ngrok_url = start_ngrok(PORT)

    # 2️⃣ 更新 Rebrandly 短網址
    update_rebrandly(ngrok_url)

    # 3️⃣ 啟動 Flask 伺服器
    app.run(host='0.0.0.0', port=PORT, debug=False) 