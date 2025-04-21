# app/services/file_service.py
import os
#import json
import uuid
import shutil
#from datetime import datetime
#from werkzeug.utils import secure_filename
#from flask import current_app
from app.utils import text_processer
import time


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
    directory_path = os.path.join("app", "data_upload", subject, "lectures")
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    file_path = os.path.join(directory_path, file.filename)
    
    # 儲存檔案
    file.save(file_path)

    # 將pdf儲存成圖片
    file_name_without_ext = file.filename.split('.')[0]
    imgs_dir_path = os.path.join(directory_path, file_name_without_ext + '_imgs')
    if not os.path.exists(imgs_dir_path):
        os.makedirs(imgs_dir_path)
    
    # 使用 pdf2image 將 PDF 轉換為圖片
    from pdf2image import convert_from_path
    images = convert_from_path(file_path)
    for i, image in enumerate(images):
        image.save(os.path.join(imgs_dir_path, f"{file_name_without_ext}_{i}.png"), "PNG")
    
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
    allowed_extensions = {'jpg', 'jpeg', 'png'} # , 'docx', 'txt', 'pdf', 
    if not allowed_file(file.filename, allowed_extensions):
        return {'success': False, 'error': f'不支援的檔案類型：{file.filename}，請上傳圖片檔案'} # 、DOCX、TXT 
    
    # 確保目標目錄存在
    target_dir = os.path.join("app", "data_upload", subject, "notes")
    os.makedirs(target_dir, exist_ok=True)
    
    # 檢查是否有同名檔案，如果有則加上時間戳
    original_filename = file.filename
    filename = original_filename
    if os.path.exists(os.path.join(target_dir, filename)):
        name, ext = os.path.splitext(original_filename)
        timestamp = int(time.time())
        filename = f"{name}_{timestamp}{ext}"
    
    # 生成id
    unique_id = str(uuid.uuid4())

    # 註冊檔案
    register_new_file(subject, "notes", filename, unique_id)

    # 建立檔案儲存路徑
    file_path = os.path.join(target_dir, filename)
    
    # 儲存檔案
    file.save(file_path)
    
    return {
        'success': True,
        'message': '檔案上傳成功',
        'save_path': file_path,
        'file_id': unique_id,
        'filename': filename
    }

# 獲取科目列表
def get_subjects():
    """獲取所有科目列表"""
    subjects = []
    
    # 檢查 data_upload 下的科目資料夾
    upload_path = os.path.join("app", "data_upload")
    server_path = os.path.join("app", "data_server")
    
    # 從 data_upload 獲取科目
    if os.path.exists(upload_path):
        for name in os.listdir(upload_path):
            full_path = os.path.join(upload_path, name)
            if os.path.isdir(full_path) and not name.startswith('.'):
                if name not in subjects:
                    subjects.append(name)
    
    # 從 data_server 獲取科目
    if os.path.exists(server_path):
        for name in os.listdir(server_path):
            full_path = os.path.join(server_path, name)
            if os.path.isdir(full_path) and not name.startswith('.'):
                if name not in subjects:
                    subjects.append(name)
    
    return subjects

# 獲取講義列表
def get_lectures(subject):
    """獲取指定科目的所有講義"""
    lectures = []
    
    # 檢查 index.json 是否存在
    index_path = os.path.join("app", "data_upload", subject, "lectures", 'index.json')
    if os.path.exists(index_path):
        # 如果 index.json 存在，讀取其中的註冊信息
        register = text_processer.read_json(index_path, default_content=[])
        lectures.extend(register)
    
    # 檢查目錄中的實際檔案
    directory_path = os.path.join("app", "data_upload", subject, "lectures")
    if os.path.exists(directory_path):
        # 獲取所有檔案
        files = [f for f in os.listdir(directory_path) 
                if os.path.isfile(os.path.join(directory_path, f)) 
                and not f.startswith('.') 
                and f != 'index.json']
        
        # 查找在目錄中但不在 index.json 中的檔案
        registered_files = [entry.get('filename', '') for entry in lectures]
        for filename in files:
            if filename not in registered_files:
                # 為找到的檔案生成一個唯一ID
                unique_id = str(uuid.uuid4())
                # 將檔案添加到列表
                lectures.append({'id': unique_id, 'filename': filename})
                # 同時更新 index.json
                register_new_file(subject, "lectures", filename, unique_id)
    
    return lectures

# 獲取筆記列表
def get_notes(subject):
    """獲取指定科目的所有筆記"""
    notes = []
    
    # 檢查 index.json 是否存在
    index_path = os.path.join("app", "data_upload", subject, "notes", 'index.json')
    if os.path.exists(index_path):
        # 如果 index.json 存在，讀取其中的註冊信息
        register = text_processer.read_json(index_path, default_content=[])
        notes.extend(register)
    
    # 檢查目錄中的實際檔案
    directory_path = os.path.join("app", "data_upload", subject, "notes")
    if os.path.exists(directory_path):
        # 獲取所有檔案
        files = [f for f in os.listdir(directory_path) 
                if os.path.isfile(os.path.join(directory_path, f)) 
                and not f.startswith('.') 
                and f != 'index.json']
        
        # 查找在目錄中但不在 index.json 中的檔案
        registered_files = [entry.get('filename', '') for entry in notes]
        for filename in files:
            if filename not in registered_files:
                # 為找到的檔案生成一個唯一ID
                unique_id = str(uuid.uuid4())
                # 將檔案添加到列表
                notes.append({'id': unique_id, 'filename': filename})
                # 同時更新 index.json
                register_new_file(subject, "notes", filename, unique_id)
    
    return notes


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
    try:
        # 遍歷所有科目，尋找匹配的講義ID
        subjects = get_subjects()
        for subject in subjects:
            index_path = os.path.join("app", "data_upload", subject, "lectures", "index.json")
            if not os.path.exists(index_path):
                continue
                
            register = text_processer.read_json(index_path, default_content=[])
            for i, entry in enumerate(register):
                if entry.get("id") == lecture_id:
                    # 找到匹配的講義
                    filename = entry.get("filename")
                    file_path = os.path.join("app", "data_upload", subject, "lectures", filename)
                    
                    # 刪除檔案（如果存在）
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    
                    # 從index.json中移除
                    register.pop(i)
                    text_processer.write_json(register, index_path)
                    
                    return {
                        'success': True, 
                        'message': f'已刪除講義：{filename}'
                    }
        
        # 如果未找到講義
        return {'success': False, 'error': '找不到指定的講義'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# 刪除筆記
def delete_note(note_id):
    """刪除指定ID的筆記"""
    try:
        # 遍歷所有科目，尋找匹配的筆記ID
        subjects = get_subjects()
        for subject in subjects:
            index_path = os.path.join("app", "data_upload", subject, "notes", "index.json")
            if not os.path.exists(index_path):
                continue
                
            register = text_processer.read_json(index_path, default_content=[])
            for i, entry in enumerate(register):
                if entry.get("id") == note_id:
                    # 找到匹配的筆記
                    filename = entry.get("filename")
                    file_path = os.path.join("app", "data_upload", subject, "notes", filename)
                    
                    # 刪除檔案（如果存在）
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    
                    # 從index.json中移除
                    register.pop(i)
                    text_processer.write_json(register, index_path)
                    
                    return {
                        'success': True, 
                        'message': f'已刪除筆記：{filename}'
                    }
        
        # 如果未找到筆記
        return {'success': False, 'error': '找不到指定的筆記'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

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

# 創建科目資料夾
def create_subject_folders(subject_name):
    """
    創建新科目所需的資料夾結構
    
    Args:
        subject_name: 科目名稱
        
    Returns:
        dict: 包含創建結果的字典
    """
    try:
        # 創建主要資料夾
        data_upload_path = os.path.join("app", "data_upload", subject_name)
        data_server_path = os.path.join("app", "data_server", subject_name)
        
        # 檢查是否已存在
        if os.path.exists(data_upload_path) or os.path.exists(data_server_path):
            return {'success': False, 'error': '該科目資料夾已存在'}
        
        # 創建 data_upload 下的資料夾結構
        os.makedirs(data_upload_path, exist_ok=True)
        os.makedirs(os.path.join(data_upload_path, "lectures"), exist_ok=True)
        os.makedirs(os.path.join(data_upload_path, "notes"), exist_ok=True)
        
        # 創建 data_server 下的資料夾
        os.makedirs(data_server_path, exist_ok=True)
        os.makedirs(os.path.join(data_server_path, "lectures"), exist_ok=True)
        os.makedirs(os.path.join(data_server_path, "notes"), exist_ok=True)
        
        # 創建 index.json 檔案
        lectures_index_path = os.path.join(data_upload_path, "lectures", "index.json")
        notes_index_path = os.path.join(data_upload_path, "notes", "index.json")
        
        # 初始化為空陣列
        text_processer.write_json([], lectures_index_path)
        text_processer.write_json([], notes_index_path)
        
        return {'success': True, 'message': '科目資料夾創建成功'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# 刪除科目資料夾及所有相關數據
def delete_subject_folders(subject_name):
    """
    刪除指定科目的所有資料夾及檔案
    
    Args:
        subject_name: 科目名稱
        
    Returns:
        dict: 包含刪除結果的字典
    """
    try:
        # 定義需要刪除的路徑
        data_upload_path = os.path.join("app", "data_upload", subject_name)
        data_server_path = os.path.join("app", "data_server", subject_name)
        
        # 檢查路徑是否存在，存在則刪除
        paths_to_delete = []
        if os.path.exists(data_upload_path):
            paths_to_delete.append(data_upload_path)
        if os.path.exists(data_server_path):
            paths_to_delete.append(data_server_path)
        
        # 如果沒有找到任何資料夾，返回錯誤
        if not paths_to_delete:
            return {'success': False, 'error': '找不到該科目的資料夾'}
        
        # 刪除所有找到的資料夾
        for path in paths_to_delete:
            shutil.rmtree(path)
        
        return {
            'success': True, 
            'message': f'已刪除科目 "{subject_name}" 的所有數據',
            'deleted_paths': paths_to_delete
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


# 刪除講義
def delete_lecture_htmx(subject, lecture_id):
    """刪除指定ID的講義"""

    # set 
    directory_upload_path = os.path.join("app", "data_upload", subject, "lectures")
    directory_server_path = os.path.join("app", "data_server", subject, "lectures")

    index_path = os.path.join(directory_upload_path, "index.json")
    register = text_processer.read_json(index_path, default_content=[])

    filename = None
    i = -1
    for idx, entry in enumerate(register):
        if entry.get("id") == lecture_id:
            filename = entry.get("filename")
            i = idx
            break
    
    if filename is None:
        return {'success': False, 'error': '找不到指定的講義'}
    
    file_name_without_ext = filename.split('.')[0]

    # 安全刪除函數
    def safe_remove(file_path):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"刪除檔案時發生錯誤: {file_path}, 錯誤: {str(e)}")

    # 安全刪除目錄
    def safe_remove_dir(dir_path):
        try:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
        except Exception as e:
            print(f"刪除目錄時發生錯誤: {dir_path}, 錯誤: {str(e)}")

    # delete upload
    imgs_dir_path = os.path.join(directory_upload_path, file_name_without_ext + '_imgs')
    safe_remove_dir(imgs_dir_path)
    safe_remove(os.path.join(directory_upload_path, filename))

    # delete server
    safe_remove(os.path.join(directory_server_path, file_name_without_ext + '.json'))
    safe_remove(os.path.join(directory_server_path, file_name_without_ext + '_keypoints.json'))
    safe_remove(os.path.join(directory_server_path, file_name_without_ext + '_topics.json'))
    safe_remove(os.path.join(directory_server_path, file_name_without_ext + '_overall_lr.json'))
    safe_remove(os.path.join(directory_server_path, file_name_without_ext + '_tree.png'))

    # delete index
    if i >= 0:
        register.pop(i)
        text_processer.write_json(register, index_path)

    return {'success': True, 'message': '已刪除講義'}

# 刪除筆記
def delete_note_htmx(subject, note_id):
    """刪除指定ID的筆記"""

    # set
    directory_upload_path = os.path.join("app", "data_upload", subject, "notes")
    directory_server_path = os.path.join("app", "data_server", subject, "notes")
    index_path = os.path.join(directory_upload_path, "index.json")
    register = text_processer.read_json(index_path, default_content=[])

    filename = None
    i = -1
    for idx, entry in enumerate(register):
        if entry.get("id") == note_id:
            filename = entry.get("filename")
            i = idx
            break
    
    if filename is None:
        return {'success': False, 'error': '找不到指定的筆記'}
    
    file_name_without_ext = filename.split('.')[0]

    # delete related note in keypoints.json
    notes_path = os.path.join(directory_server_path, file_name_without_ext + '.json')
    if  os.path.exists(notes_path):
        notes_json = text_processer.read_json(notes_path, default_content={})

        if 'Lecture_Name' in notes_json:
            keypoint_name = notes_json['Lecture_Name']
            keypoint_name_without_ext = keypoint_name.split('.')[0]
            keypoint_path = os.path.join("app", "data_server", subject, "lectures", keypoint_name_without_ext, "keypoints.json")

            if os.path.exists(keypoint_path):
                keypoint_json = text_processer.read_json(keypoint_path, default_content={})

                for note in notes_json['Notes']:
                    k_idx = note['Keypoint_id']
                    for note_kp in keypoint_json[k_idx]['Notes']:
                        if note_kp['Title'] == note['Title']:
                            keypoint_json[k_idx]['Notes'].remove(note_kp)

                text_processer.write_json(keypoint_json, keypoint_path)

    # 安全刪除函數
    def safe_remove(file_path):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"刪除檔案時發生錯誤: {file_path}, 錯誤: {str(e)}")

    # delete upload
    safe_remove(os.path.join(directory_upload_path, filename))

    # delete server
    safe_remove(os.path.join(directory_server_path, file_name_without_ext + '.json'))
    safe_remove(os.path.join(directory_server_path, file_name_without_ext + '_lines_bounding_box.png'))

    # delete index
    if i >= 0:
        register.pop(i)
        text_processer.write_json(register, index_path)

    return {'success': True, 'message': '已刪除筆記'}

