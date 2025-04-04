# app/routes/upload.py
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from app.services.file_service import (
    upload_lecture, upload_note, get_subjects, get_lectures, get_notes,
    get_lecture, get_note, delete_lecture, delete_note, get_notes_for_lecture
)

# 創建藍圖
upload_bp = Blueprint('upload', __name__, url_prefix='/api/upload')

# 獲取所有科目
@upload_bp.route('/subjects', methods=['GET'])
def subjects():
    """獲取所有科目列表"""
    return jsonify(get_subjects())

# 上傳講義
@upload_bp.route('/lecture', methods=['POST'])
def upload_lecture_route():
    """上傳講義檔案"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '沒有文件部分'}), 400
    
    file = request.files['file']
    subject = request.form.get('subject')
    
    if not subject:
        return jsonify({'success': False, 'error': '請提供科目名稱'}), 400
    
    result = upload_lecture(file, subject)
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400

# 上傳筆記
@upload_bp.route('/note', methods=['POST'])
def upload_note_route():
    """上傳筆記檔案"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '沒有文件部分'}), 400
    
    file = request.files['file']
    subject = request.form.get('subject')
    lecture_id = request.form.get('lecture_id')
    
    if not subject:
        return jsonify({'success': False, 'error': '請提供科目名稱'}), 400
    
    result = upload_note(file, subject, lecture_id)
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400

# 獲取特定科目的所有講義
@upload_bp.route('/lectures/<subject>', methods=['GET'])
def lectures(subject):
    """獲取指定科目的所有講義"""
    return jsonify(get_lectures(subject))

# 獲取特定科目的所有筆記
@upload_bp.route('/notes/<subject>', methods=['GET'])
def notes(subject):
    """獲取指定科目的所有筆記"""
    return jsonify(get_notes(subject))

# 獲取特定講義相關的所有筆記
@upload_bp.route('/lecture/<lecture_id>/notes', methods=['GET'])
def lecture_notes(lecture_id):
    """獲取與特定講義相關的所有筆記"""
    return jsonify(get_notes_for_lecture(lecture_id))

# 刪除講義
@upload_bp.route('/lecture/<lecture_id>', methods=['DELETE'])
def delete_lecture_route(lecture_id):
    """刪除講義"""
    result = delete_lecture(lecture_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 404

# 刪除筆記
@upload_bp.route('/note/<note_id>', methods=['DELETE'])
def delete_note_route(note_id):
    """刪除筆記"""
    result = delete_note(note_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 404


@upload_bp.route('/test-lecture', methods=['POST'])
def upload_lecture_test():
    """測試上傳講義檔案"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '沒有檔案部分'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': '沒有選擇檔案'}), 400
    
    # 保存檔案
    result = save_uploaded_file(current_app, file, 'lecture')
    
    return jsonify(result)

@upload_bp.route('/test-note', methods=['POST'])
def upload_note_test():
    """測試上傳筆記檔案"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '沒有檔案部分'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': '沒有選擇檔案'}), 400
    
    # 保存檔案
    result = save_uploaded_file(current_app, file, 'note')
    
    return jsonify(result)