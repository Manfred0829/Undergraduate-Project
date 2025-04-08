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
    
    # 註冊藍圖
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.upload import upload_bp
    # from app.routes.process import process_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(upload_bp)
    # app.register_blueprint(process_bp)
    
    return app