from flask import Flask, render_template
import os

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
    # 啟動開發伺服器
    print("HTMX 版本伺服器已啟動，訪問 http://localhost:5000 查看效果")
    app.run(debug=True, host='0.0.0.0', port=5000) 