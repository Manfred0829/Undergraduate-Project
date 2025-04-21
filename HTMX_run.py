from flask import Flask, render_template
import os
import sys
import argparse
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

def check_process():
    
    from app.services import file_service
    #file_service.update_file_status("組合語言_test", "lectures", "w1_introduction.pdf", "error")
    
    return

if __name__ == "__main__":
    # 解析命令行參數
    parser = argparse.ArgumentParser(description='啟動HTMX應用程式')
    parser.add_argument('mode', nargs='?', default='public', 
                      help='執行模式: "public" 對外公開 (預設), "test" 僅內網訪問')
    args = parser.parse_args()
    
    app = create_app()
    
    # 檢查是否為測試模式
    if args.mode.lower() == 'test':
        # 測試模式，僅在內網運行
        print("測試模式：僅在內網運行，訪問 http://localhost:5001 查看效果")
        app.run(debug=True, host='0.0.0.0', port=PORT)
    elif args.mode.lower() == 'check':
        # 檢查模式，不開啟伺服器，僅執行固定檢查流程
        print("檢查模式：不開啟伺服器，僅執行固定檢查流程")
        check_process()

    else:
        # 對外公開模式
        # 1️⃣ 啟動 ngrok 並取得公開網址
        ngrok_url = start_ngrok(PORT)
        
        # 2️⃣ 更新 Rebrandly 短網址
        update_rebrandly(ngrok_url)
        
        # 3️⃣ 啟動 Flask 伺服器
        print("HTMX 版本伺服器已啟動，訪問 http://localhost:5001 查看效果")
        print(f"公網網址: {ngrok_url}")
        app.run(debug=False, host='0.0.0.0', port=PORT) 