from flask import Flask, render_template
import os
from app.services.ngrok_service import start_ngrok
from app.services.rebrandly_service import update_rebrandly

# 設定端口
PORT = 5001

def create_app():
    """創建 Flask 應用並註冊相關配置"""
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app'),
                static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/static'))
    
    # 註冊 HTMX 路由
    from app.HTMX_routes import register_htmx_routes
    register_htmx_routes(app)
    
    # 重定向根路徑到 HTMX 版本
    @app.route('/')
    def index():
        return render_template('HTMX_templates/login_interface.html')
    
    # 註冊必要的靜態資源路由（如有需要）
    
    return app

if __name__ == "__main__":
    app = create_app()
    
    # 1️⃣ 啟動 ngrok 並取得公開網址
    #ngrok_url = start_ngrok(PORT)
    
    # 2️⃣ 更新 Rebrandly 短網址
    #update_rebrandly(ngrok_url)
    
    # 3️⃣ 啟動 Flask 伺服器
    print("HTMX 版本伺服器已啟動，訪問 http://localhost:5001 查看效果")
    #print(f"公網網址: {ngrok_url}")
    app.run(debug=False, host='0.0.0.0', port=PORT) 