# app/routes/process.py
from flask import Blueprint, request, jsonify
from app.services.file_service import get_file_name_from_id
import os
import json

# 創建藍圖
process_bp = Blueprint('process', __name__, url_prefix='/htmx/process')

# 處理狀態緩存
# 使用字典存儲處理狀態：{file_id: {'status': 'processing|completed|error', 'error': '錯誤訊息'}}
processing_status = {}

# 獲取處理狀態
@process_bp.route('/status/<file_type>/<file_id>', methods=['GET'])
def get_processing_status(file_type, file_id):
    """
    獲取檔案處理狀態
    
    Args:
        file_type: 檔案類型 (lecture 或 note)
        file_id: 檔案ID
    
    Returns:
        處理狀態：processing, completed 或 error
    """
    # 如果狀態在緩存中存在，直接返回
    if file_id in processing_status:
        return jsonify(processing_status[file_id])
    
    # 否則檢查處理後的檔案是否存在
    # 先根據 file_id 獲取原始檔案名稱
    subject = request.args.get('subject', '')
    if not subject:
        return jsonify({'status': 'error', 'error': '缺少科目參數'}), 400
    
    filename = get_file_name_from_id(subject, 'lectures' if file_type == 'lecture' else 'notes', file_id)
    if not filename:
        return jsonify({'status': 'error', 'error': '找不到該ID對應的檔案'}), 404
    
    # 根據檔案類型檢查處理後的檔案
    file_without_ext = os.path.splitext(filename)[0]
    
    if file_type == 'lecture':
        # 講義檔案處理後會生成 JSON 檔案
        processed_path = os.path.join('app', 'data_server', subject, 'lectures', f"{file_without_ext}.json")
        keypoints_path = os.path.join('app', 'data_server', subject, 'lectures', f"{file_without_ext}_keypoints.json")
        
        if os.path.exists(processed_path) and os.path.exists(keypoints_path):
            # 檢查檔案是否有內容
            try:
                with open(processed_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                with open(keypoints_path, 'r', encoding='utf-8') as f:
                    keypoints = json.load(f)
                
                if data and keypoints:
                    # 處理完成
                    processing_status[file_id] = {'status': 'completed'}
                    return jsonify({'status': 'completed'})
            except:
                pass
    else:  # note
        # 筆記檔案處理後會生成 JSON 檔案
        processed_path = os.path.join('app', 'data_server', subject, 'notes', f"{file_without_ext}.json")
        
        if os.path.exists(processed_path):
            # 檢查檔案是否有內容
            try:
                with open(processed_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if data:
                    # 處理完成
                    processing_status[file_id] = {'status': 'completed'}
                    return jsonify({'status': 'completed'})
            except:
                pass
    
    # 如果文件不存在或無法讀取，則假設仍在處理中
    return jsonify({'status': 'processing'})

# 檢查是否有新檔案
@process_bp.route('/check-new-files/<subject>', methods=['GET'])
def check_new_files(subject):
    """檢查是否有新檔案的API端點"""
    # 這個功能可以實現為檢查最新修改時間或檔案計數等
    # 目前只是一個簡單的佔位實現
    return jsonify({'has_new_files': False})

# 設置處理狀態 (內部使用)
def set_processing_status(file_id, status, error=None):
    """
    設置處理狀態
    
    Args:
        file_id: 檔案ID
        status: 狀態 (processing, completed, error)
        error: 錯誤訊息
    """
    status_data = {'status': status}
    if error:
        status_data['error'] = str(error)
    
    processing_status[file_id] = status_data 