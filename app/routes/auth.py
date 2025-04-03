from flask import Blueprint, render_template, redirect, url_for

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def login_interface():
    return render_template('login_interface.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    return redirect(url_for('main.user_interface')) 