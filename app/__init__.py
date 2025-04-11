from flask import Flask
from config import Config
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 確保資料目錄存在
    data_dir = os.path.join(app.root_path, 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        os.makedirs(os.path.join(data_dir, 'json'))
        os.makedirs(os.path.join(data_dir, 'uploads'))
        os.makedirs(os.path.join(data_dir, 'uploads', 'lectures'))
        os.makedirs(os.path.join(data_dir, 'uploads', 'notes'))
        os.makedirs(os.path.join(data_dir, 'ocr'))
        os.makedirs(os.path.join(data_dir, 'vectors'))
    
    # 提供data_server目錄下的靜態文件訪問
    data_server_dir = os.path.join(app.root_path, 'data_server')
    app.config['DATA_SERVER_DIR'] = data_server_dir
    app.static_folder = 'static'
    
    # 註冊靜態文件服務路由
    from flask import send_from_directory
    
    @app.route('/data_server/<path:subject>/lectures/<path:filename>')
    def serve_lecture_files(subject, filename):
        path = os.path.join(data_server_dir, subject, 'lectures')
        return send_from_directory(path, filename)
    
    # 註冊藍圖
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.upload import upload_bp
    from app.routes.process import process_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(process_bp)
    
    return app