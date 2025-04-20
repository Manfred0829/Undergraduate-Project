from flask import Blueprint, render_template, redirect, url_for

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def login_interface():
    return render_template('login_interface.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    # 在此可以添加實際的登入驗證邏輯
    # 成功登入後，重定向到主界面
    return redirect('/htmx/main') 