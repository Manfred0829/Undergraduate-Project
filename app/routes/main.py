from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/user_interface')
def user_interface():
    return render_template('user_interface.html') 