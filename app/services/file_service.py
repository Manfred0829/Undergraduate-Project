# app/services/file_service.py
import os
#import json
import uuid
#import shutil
#from datetime import datetime
#from werkzeug.utils import secure_filename
#from flask import current_app
from app.utils import text_processer


def register_new_file(subject,type,filename,unique_id):
    path = os.path.join("app", "data_upload", subject, type, 'index.json')
    register = text_processer.read_json(path, default_content=[])

    entry = {"id": unique_id, "filename": filename}
    register.append(entry)

    text_processer.write_json(register, path)

def get_file_name_from_id(subject, type, unique_id):
    path = os.path.join("app", "data_upload", subject, type, 'index.json')
    
    # 載入 index.json
    register = text_processer.read_json(path, default_content=[])
    
    # 遍歷列表找對應的 id
    for entry in register:
        if entry.get("id") == unique_id:
            return entry.get("filename")
    
    # 若未找到，回傳 None 或拋出錯誤
    return None  # 或 raise ValueError(f"No file found for ID: {unique_id}")


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
    allowed_extensions = {'pdf'} # , 'docx', 'ppt', 'pptx', 'txt'
    if not allowed_file(file.filename, allowed_extensions):
        return {'success': False, 'error': '不支援的檔案類型，請上傳 PDF檔案'} # 、DOCX、PPT、PPTX 或 TXT 
    
    # 生成id
    unique_id = str(uuid.uuid4())

    # 註冊檔案
    register_new_file(subject,"lectures",file.filename,unique_id)

    # 建立檔案儲存路徑
    file_path = os.path.join("app", "data_upload", subject, "lectures", file.filename)
    
    # 儲存檔案
    file.save(file_path)
    
    return {'success': True, 
            'message': '檔案上傳成功',
            'save_path': file_path,
            'file_id': unique_id
            }

# 上傳筆記
def upload_note(file, subject):
    """
    上傳筆記檔案
    
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
    allowed_extensions = {'pdf', 'jpg', 'jpeg', 'png'} # , 'docx', 'txt'
    if not allowed_file(file.filename, allowed_extensions):
        return {'success': False, 'error': '不支援的檔案類型，請上傳 PDF或圖片檔案'} # 、DOCX、TXT 
    
    # 生成id
    unique_id = str(uuid.uuid4())

    # 註冊檔案
    register_new_file(subject,"notes",file.filename,unique_id)

    # 建立檔案儲存路徑
    file_path = os.path.join("app", "data_upload", subject, "notes", file.filename)
    
    # 儲存檔案
    file.save(file_path)
    
    
    return {
        'success': True,
        'message': '檔案上傳成功',
        'save_path': file_path,
        'file_id': unique_id
    }

# 獲取科目列表
def get_subjects():
    """獲取所有科目列表"""
    subjects = []
    path = os.path.join("app", "data_server")

    for name in os.listdir(path):
        full_path = os.path.join(path, name)
        if os.path.isdir(full_path):
            subjects.append(name)

    return subjects

# 獲取講義列表
def get_lectures(subject):
    """獲取指定科目的所有講義"""
    path = os.path.join("app", "data_upload", subject, "lectures", 'index.json')
    register = text_processer.read_json(path, default_content=[])

    return register

# 獲取筆記列表
def get_notes(subject):
    """獲取指定科目的所有筆記"""
    path = os.path.join("app", "data_upload", subject, "notes", 'index.json')
    register = text_processer.read_json(path, default_content=[])

    return register


# 獲取特定講義
def get_lecture(subject, lecture_id):
    """獲取指定ID的講義"""

    name = get_file_name_from_id(subject, "lectures", lecture_id)
    if name is None:
        return None  # 或者 raise ValueError("Lecture not found.")

    path = os.path.join("app", "data_upload", subject, "lectures", name)

    # 根據檔案類型讀取
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    return content


# 獲取特定筆記
def get_note(subject,note_id):
    """獲取指定ID的筆記"""

    name = get_file_name_from_id(subject, "lectures", note_id)
    if name is None:
        return None  # 或者 raise ValueError("Lecture not found.")

    path = os.path.join("app", "data_upload", subject, "notes", name)

    # 根據檔案類型讀取
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    return content

# 刪除講義
def delete_lecture(lecture_id):
    """刪除指定ID的講義"""
    '''
    json_path = os.path.join(current_app.root_path, 'data_json', 'lectures.json')
    lectures = read_json(json_path, default_content={})
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
    notes_path = os.path.join(current_app.root_path, 'data_json', 'notes.json')
    notes = read_json(notes_path, default_content={})
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
    write_json(lectures, json_path)
    write_json(notes, notes_path)
    
    return {'success': True}
    '''
    return {'success': False}

# 刪除筆記
def delete_note(note_id):
    """刪除指定ID的筆記"""
    '''
    json_path = os.path.join(current_app.root_path, 'data_json', 'notes.json')
    notes = read_json(json_path, default_content={})
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
    write_json(notes, json_path)
    
    return {'success': True}
    '''
    return {'success': False}

# 獲取特定講義的所有相關筆記
def get_notes_for_lecture(lecture_id):
    """獲取與特定講義相關的所有筆記"""
    '''
    json_path = os.path.join(current_app.root_path, 'data_json', 'notes.json')
    notes = read_json(json_path, default_content={})
    related_notes = []
    
    for subject in notes:
        for note in notes[subject]:
            if note.get('lecture_id') == lecture_id:
                related_notes.append(note)
    
    return related_notes
    '''
    return None