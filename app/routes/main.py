from flask import Blueprint, render_template, jsonify
from app.services.file_service import get_subjects, get_lectures, get_notes

main_bp = Blueprint('main', __name__)

@main_bp.route('/user_interface')
def user_interface():
    # 獲取科目列表以提供給前端
    subjects = get_subjects()
    
    return render_template('user_interface.html')

@main_bp.route('/api/subjects')
def api_subjects():
    """API端點：獲取所有科目"""
    return jsonify(get_subjects())

@main_bp.route('/api/lectures/<subject>')
def api_lectures(subject):
    """API端點：獲取指定科目的所有講義"""
    return jsonify(get_lectures(subject))

@main_bp.route('/api/notes/<subject>')
def api_notes(subject):
    """API端點：獲取指定科目的所有筆記"""
    return jsonify(get_notes(subject)) 