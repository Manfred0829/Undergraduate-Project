# app/services/file_service.py
import os
import json
import uuid
import shutil
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app

# 確保數據目錄存在
def ensure_data_directories():
    """確保所有需要的數據目錄存在"""
    base_dir = os.path.join(current_app.root_path, 'data')
    
    # 確保基礎目錄存在
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    # 確保JSON數據目錄存在
    json_dir = os.path.join(base_dir, 'json')
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)
    
    # 確保上傳文件目錄存在
    uploads_dir = os.path.join(base_dir, 'uploads')
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        
    # 確保講義和筆記目錄存在
    lectures_dir = os.path.join(uploads_dir, 'lectures')
    if not os.path.exists(lectures_dir):
        os.makedirs(lectures_dir)
        
    notes_dir = os.path.join(uploads_dir, 'notes')
    if not os.path.exists(notes_dir):
        os.makedirs(notes_dir)
        
    # 確保文字辨識結果目錄存在
    ocr_dir = os.path.join(base_dir, 'ocr')
    if not os.path.exists(ocr_dir):
        os.makedirs(ocr_dir)
        
    # 確保向量嵌入結果目錄存在
    vectors_dir = os.path.join(base_dir, 'vectors')
    if not os.path.exists(vectors_dir):
        os.makedirs(vectors_dir)
    
    return {
        'base': base_dir,
        'json': json_dir,
        'uploads': uploads_dir,
        'lectures': lectures_dir,
        'notes': notes_dir,
        'ocr': ocr_dir,
        'vectors': vectors_dir
    }

# 讀取JSON數據
def read_json(filename):
    """從JSON檔案讀取數據，如果檔案不存在則返回空數據"""
    json_path = os.path.join(current_app.root_path, 'data', 'json', filename)
    
    if not os.path.exists(json_path):
        return {}
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 寫入JSON數據
def write_json(filename, data):
    """將數據寫入JSON檔案"""
    dirs = ensure_data_directories()
    json_path = os.path.join(dirs['json'], filename)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 檢查檔案類型是否允許
def allowed_file(filename, allowed_extensions):
    """檢查檔案是否有允許的擴展名"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

# 上傳講義
def upload_lecture(file, subject):
    """
    上傳講義檔案
    
    Args:
        file: 上傳的檔案物件
        subject: 科目名稱
        
    Returns:
        dict: 包含上傳結果的字典
    """
    # 檢查檔案是否有效
    if file is None or file.filename == '':
        return {'success': False, 'error': '沒有選擇檔案'}
    
    # 檢查檔案類型
    allowed_extensions = {'pdf', 'docx', 'ppt', 'pptx', 'txt'}
    if not allowed_file(file.filename, allowed_extensions):
        return {'success': False, 'error': '不支援的檔案類型，請上傳 PDF、DOCX、PPT、PPTX 或 TXT 檔案'}
    
    # 確保目錄存在
    dirs = ensure_data_directories()
    
    # 生成安全的檔名
    original_filename = secure_filename(file.filename)
    file_extension = original_filename.rsplit('.', 1)[1].lower()
    unique_id = str(uuid.uuid4())
    unique_filename = f"{unique_id}.{file_extension}"
    
    # 建立檔案儲存路徑
    subject_dir = os.path.join(dirs['lectures'], subject)
    if not os.path.exists(subject_dir):
        os.makedirs(subject_dir)
    
    file_path = os.path.join(subject_dir, unique_filename)
    
    # 儲存檔案
    file.save(file_path)
    
    # 獲取檔案大小
    file_size = os.path.getsize(file_path)
    
    # 建立檔案記錄
    lecture_data = {
        'id': unique_id,
        'original_filename': original_filename,
        'filename': unique_filename,
        'file_path': file_path,
        'file_size': file_size,
        'file_type': file_extension,
        'subject': subject,
        'upload_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'ocr_processed': False,
        'ocr_text_path': None,
        'vector_embeddings': None
    }
    
    # 讀取現有講義數據
    lectures = read_json('lectures.json')
    
    # 確保存在subject鍵
    if subject not in lectures:
        lectures[subject] = []
    
    # 添加新講義
    lectures[subject].append(lecture_data)
    
    # 儲存更新後的數據
    write_json('lectures.json', lectures)
    
    return {
        'success': True,
        'lecture': lecture_data
    }

# 上傳筆記
def upload_note(file, subject, lecture_id=None):
    """
    上傳筆記檔案
    
    Args:
        file: 上傳的檔案物件
        subject: 科目名稱
        lecture_id: 關聯的講義ID (可選)
        
    Returns:
        dict: 包含上傳結果的字典
    """
    # 檢查檔案是否有效
    if file is None or file.filename == '':
        return {'success': False, 'error': '沒有選擇檔案'}
    
    # 檢查檔案類型
    allowed_extensions = {'pdf', 'docx', 'txt', 'jpg', 'jpeg', 'png'}
    if not allowed_file(file.filename, allowed_extensions):
        return {'success': False, 'error': '不支援的檔案類型，請上傳 PDF、DOCX、TXT 或圖片檔案'}
    
    # 確保目錄存在
    dirs = ensure_data_directories()
    
    # 生成安全的檔名
    original_filename = secure_filename(file.filename)
    file_extension = original_filename.rsplit('.', 1)[1].lower()
    unique_id = str(uuid.uuid4())
    unique_filename = f"{unique_id}.{file_extension}"
    
    # 建立檔案儲存路徑
    subject_dir = os.path.join(dirs['notes'], subject)
    if not os.path.exists(subject_dir):
        os.makedirs(subject_dir)
    
    file_path = os.path.join(subject_dir, unique_filename)
    
    # 儲存檔案
    file.save(file_path)
    
    # 獲取檔案大小
    file_size = os.path.getsize(file_path)
    
    # 建立檔案記錄
    note_data = {
        'id': unique_id,
        'original_filename': original_filename,
        'filename': unique_filename,
        'file_path': file_path,
        'file_size': file_size,
        'file_type': file_extension,
        'subject': subject,
        'lecture_id': lecture_id,
        'upload_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'ocr_processed': False,
        'ocr_text_path': None,
        'vector_embeddings': None
    }
    
    # 讀取現有筆記數據
    notes = read_json('notes.json')
    
    # 確保存在subject鍵
    if subject not in notes:
        notes[subject] = []
    
    # 添加新筆記
    notes[subject].append(note_data)
    
    # 儲存更新後的數據
    write_json('notes.json', notes)
    
    return {
        'success': True,
        'note': note_data
    }

# 獲取科目列表
def get_subjects():
    """獲取所有科目列表"""
    subjects = []
    
    # 從講義數據獲取科目
    lectures = read_json('lectures.json')
    for subject in lectures.keys():
        if subject not in subjects:
            subjects.append(subject)
    
    # 從筆記數據獲取科目
    notes = read_json('notes.json')
    for subject in notes.keys():
        if subject not in subjects:
            subjects.append(subject)
    
    return subjects

# 獲取講義列表
def get_lectures(subject):
    """獲取指定科目的所有講義"""
    lectures = read_json('lectures.json')
    
    if subject not in lectures:
        return []
    
    return lectures[subject]

# 獲取筆記列表
def get_notes(subject):
    """獲取指定科目的所有筆記"""
    notes = read_json('notes.json')
    
    if subject not in notes:
        return []
    
    return notes[subject]

# 獲取特定講義
def get_lecture(lecture_id):
    """獲取指定ID的講義"""
    lectures = read_json('lectures.json')
    
    for subject in lectures:
        for lecture in lectures[subject]:
            if lecture['id'] == lecture_id:
                return lecture
    
    return None

# 獲取特定筆記
def get_note(note_id):
    """獲取指定ID的筆記"""
    notes = read_json('notes.json')
    
    for subject in notes:
        for note in notes[subject]:
            if note['id'] == note_id:
                return note
    
    return None

# 刪除講義
def delete_lecture(lecture_id):
    """刪除指定ID的講義"""
    lectures = read_json('lectures.json')
    lecture_to_delete = None
    subject_of_lecture = None
    
    # 尋找要刪除的講義
    for subject in lectures:
        for i, lecture in enumerate(lectures[subject]):
            if lecture['id'] == lecture_id:
                lecture_to_delete = lecture
                subject_of_lecture = subject
                lectures[subject].pop(i)
                break
        if lecture_to_delete:
            break
    
    if not lecture_to_delete:
        return {'success': False, 'error': '找不到指定的講義'}
    
    # 刪除關聯的筆記的講義ID
    notes = read_json('notes.json')
    for subject in notes:
        for note in notes[subject]:
            if note.get('lecture_id') == lecture_id:
                note['lecture_id'] = None
    
    # 刪除檔案
    try:
        if os.path.exists(lecture_to_delete['file_path']):
            os.remove(lecture_to_delete['file_path'])
        
        # 如果存在OCR文本，也刪除
        if lecture_to_delete.get('ocr_text_path') and os.path.exists(lecture_to_delete['ocr_text_path']):
            os.remove(lecture_to_delete['ocr_text_path'])
    except Exception as e:
        # 即使刪除檔案失敗，仍繼續刪除記錄
        print(f"刪除檔案時出錯: {str(e)}")
    
    # 更新JSON數據
    write_json('lectures.json', lectures)
    write_json('notes.json', notes)
    
    return {'success': True}

# 刪除筆記
def delete_note(note_id):
    """刪除指定ID的筆記"""
    notes = read_json('notes.json')
    note_to_delete = None
    subject_of_note = None
    
    # 尋找要刪除的筆記
    for subject in notes:
        for i, note in enumerate(notes[subject]):
            if note['id'] == note_id:
                note_to_delete = note
                subject_of_note = subject
                notes[subject].pop(i)
                break
        if note_to_delete:
            break
    
    if not note_to_delete:
        return {'success': False, 'error': '找不到指定的筆記'}
    
    # 刪除檔案
    try:
        if os.path.exists(note_to_delete['file_path']):
            os.remove(note_to_delete['file_path'])
        
        # 如果存在OCR文本，也刪除
        if note_to_delete.get('ocr_text_path') and os.path.exists(note_to_delete['ocr_text_path']):
            os.remove(note_to_delete['ocr_text_path'])
    except Exception as e:
        # 即使刪除檔案失敗，仍繼續刪除記錄
        print(f"刪除檔案時出錯: {str(e)}")
    
    # 更新JSON數據
    write_json('notes.json', notes)
    
    return {'success': True}

# 獲取特定講義的所有相關筆記
def get_notes_for_lecture(lecture_id):
    """獲取與特定講義相關的所有筆記"""
    notes = read_json('notes.json')
    related_notes = []
    
    for subject in notes:
        for note in notes[subject]:
            if note.get('lecture_id') == lecture_id:
                related_notes.append(note)
    
    return related_notes

# 更新OCR處理狀態和結果
def update_ocr_result(file_type, file_id, ocr_text_path):
    """
    更新文件的OCR處理狀態和結果
    
    Args:
        file_type: 'lecture' 或 'note'
        file_id: 文件ID
        ocr_text_path: OCR文本文件路徑
    
    Returns:
        bool: 是否成功更新
    """
    if file_type == 'lecture':
        data = read_json('lectures.json')
        for subject in data:
            for lecture in data[subject]:
                if lecture['id'] == file_id:
                    lecture['ocr_processed'] = True
                    lecture['ocr_text_path'] = ocr_text_path
                    write_json('lectures.json', data)
                    return True
    else:  # note
        data = read_json('notes.json')
        for subject in data:
            for note in data[subject]:
                if note['id'] == file_id:
                    note['ocr_processed'] = True
                    note['ocr_text_path'] = ocr_text_path
                    write_json('notes.json', data)
                    return True
    
    return False

# 更新向量嵌入結果
def update_vector_embedding(file_type, file_id, embedding_data):
    """
    更新文件的向量嵌入結果
    
    Args:
        file_type: 'lecture' 或 'note'
        file_id: 文件ID
        embedding_data: 向量嵌入數據或文件路徑
    
    Returns:
        bool: 是否成功更新
    """
    if file_type == 'lecture':
        data = read_json('lectures.json')
        for subject in data:
            for lecture in data[subject]:
                if lecture['id'] == file_id:
                    lecture['vector_embeddings'] = embedding_data
                    write_json('lectures.json', data)
                    return True
    else:  # note
        data = read_json('notes.json')
        for subject in data:
            for note in data[subject]:
                if note['id'] == file_id:
                    note['vector_embeddings'] = embedding_data
                    write_json('notes.json', data)
                    return True
    
    return False