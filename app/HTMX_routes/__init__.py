from app.HTMX_routes.routes import htmx_bp
from app.HTMX_routes.upload import upload_bp
from app.HTMX_routes.process import process_bp

def register_htmx_routes(app):
    """註冊 HTMX 相關的路由到 Flask 應用"""
    app.register_blueprint(htmx_bp) 
    app.register_blueprint(upload_bp)
    app.register_blueprint(process_bp)
