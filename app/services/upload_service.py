import os
import json
import uuid
from datetime import datetime

def ensure_upload_directories(app):
    """確保所有上傳目錄存在"""
    # 基本的上傳目錄
    upload_dir = os.path.join(app.root_path, 'uploads')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    # 講義和筆記目錄
    lectures_dir = os.path.join(upload_dir, 'lectures')
    if not os.path.exists(lectures_dir):
        os.makedirs(lectures_dir)
    
    notes_dir = os.path.join(upload_dir, 'notes')
    if not os.path.exists(notes_dir):
        os.makedirs(notes_dir)
    
    # 記錄檔案的JSON資料
    json_dir = os.path.join(app.root_path, 'data')
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)
    
    return {
        'upload_dir': upload_dir,
        'lectures_dir': lectures_dir,
        'notes_dir': notes_dir,
        'json_dir': json_dir
    }

def save_uploaded_file(app, file, file_type):
    """
    保存上傳的檔案
    
    Args:
        app: Flask app實例
        file: 上傳的檔案物件
        file_type: 'lecture' 或 'note'
        
    Returns:
        dict: 包含上傳結果的字典
    """
    if file.filename == '':
        return {'success': False, 'message': '沒有選擇檔案'}
    
    # 取得安全的檔名
    filename = file.filename
    file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    # 生成新的檔名，避免衝突
    unique_filename = f"{str(uuid.uuid4())}.{file_ext}"
    
    # 確保目錄存在
    dirs = ensure_upload_directories(app)
    
    # 決定保存路徑
    if file_type == 'lecture':
        save_path = os.path.join(dirs['lectures_dir'], unique_filename)
        json_path = os.path.join(dirs['json_dir'], 'lectures.json')
    else:  # note
        save_path = os.path.join(dirs['notes_dir'], unique_filename)
        json_path = os.path.join(dirs['json_dir'], 'notes.json')
    
    # 保存檔案
    file.save(save_path)
    
    # 記錄檔案資訊
    file_info = {
        'id': str(uuid.uuid4()),
        'original_filename': filename,
        'saved_filename': unique_filename,
        'path': save_path,
        'size': os.path.getsize(save_path),
        'upload_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # 讀取現有檔案記錄
    try:
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []
    except:
        data = []
    
    # 添加新記錄
    data.append(file_info)
    
    # 保存更新後的記錄
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return {
        'success': True, 
        'message': '檔案上傳成功',
        'file_info': file_info
    }
