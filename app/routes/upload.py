# app/routes/upload.py
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from app.services.file_service import (
    upload_lecture, upload_note, get_subjects, get_lectures, get_notes,
    get_lecture, get_note, delete_lecture, delete_note, get_notes_for_lecture
)
from app.services import main_processer
from app.routes.process import set_processing_status
import os
import threading

# 創建藍圖
upload_bp = Blueprint('upload', __name__, url_prefix='/api/upload')

def process_lecture_async(subject, file_path, file_id):
    """
    非同步處理講義
    
    Args:
        subject: 科目名稱
        file_path: 檔案路徑
        file_id: 檔案ID
    """
    try:
        # 設置處理中狀態
        set_processing_status(file_id, 'processing')
        
        # 進行實際處理
        result = main_processer.processing_lecture(subject, file_path)
        
        # 根據處理結果設置狀態
        if result['success']:
            set_processing_status(file_id, 'completed')
        else:
            set_processing_status(file_id, 'error', result['error'])
    
    except Exception as e:
        # 處理過程中出現錯誤
        set_processing_status(file_id, 'error', str(e))

def process_note_async(subject, lecture_name, file_path, file_id):
    """
    非同步處理筆記
    
    Args:
        subject: 科目名稱
        file_path: 檔案路徑
        file_id: 檔案ID
    """
    try:
        # 設置處理中狀態
        set_processing_status(file_id, 'processing')
        
        # 進行實際處理
        result = main_processer.processing_note(subject, lecture_name, file_path)
        
        # 根據處理結果設置狀態
        if result['success']:
            set_processing_status(file_id, 'completed')
        else:
            set_processing_status(file_id, 'error', result['error'])
    
    except Exception as e:
        # 處理過程中出現錯誤
        set_processing_status(file_id, 'error', str(e))

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
        # 非同步處理講義文件
        thread = threading.Thread(
            target=process_lecture_async,
            args=(subject, result['save_path'], result['file_id'])
        )
        thread.daemon = True
        thread.start()
        
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
    lecture_name = request.form.get('lecture_name')
    
    if not subject:
        return jsonify({'success': False, 'error': '請提供科目名稱'}), 400
    
    result = upload_note(file, subject)
    
    if result['success']:
        # 非同步處理筆記文件
        thread = threading.Thread(
            target=process_note_async,
            args=(subject, lecture_name, result['save_path'], result['file_id'])
        )
        thread.daemon = True
        thread.start()
        
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
    


'''
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

'''

# 下載檔案
@upload_bp.route('/download/<file_type>/<subject>/<file_id>', methods=['GET'])
def download_file(file_type, subject, file_id):
    """下載檔案"""
    if file_type not in ['lectures', 'notes']:
        return jsonify({'success': False, 'error': '不支持的檔案類型'}), 400
    
    try:
        # 獲取檔案名稱
        filename = get_file_name_from_id(subject, file_type, file_id)
        if not filename:
            return jsonify({'success': False, 'error': '找不到該檔案'}), 404
        
        # 檔案路徑
        file_path = os.path.join("app", "data_upload", subject, file_type, filename)
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': '檔案不存在'}), 404
        
        # 獲取檔案所在目錄
        directory = os.path.dirname(file_path)
        
        # 使用 Flask 的 send_from_directory 函數下載檔案
        return send_from_directory(directory, filename, as_attachment=True)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500