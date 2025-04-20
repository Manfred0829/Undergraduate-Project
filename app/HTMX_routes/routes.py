from flask import Blueprint, render_template, request, jsonify, send_file, redirect
import os
import json
from app.services.file_service import get_subjects, get_lectures, get_notes, get_notes_for_lecture, create_subject_folders, delete_subject_folders
from app.services.main_processer import processing_get_keypoints, processing_get_page_info, processing_get_questions, processing_update_weights, processing_get_notes, processing_get_history, processing_update_topics
from app.utils.media_processer import get_num_pages
# 創建 Blueprint
htmx_bp = Blueprint('htmx', __name__, url_prefix='/htmx')

# 重定向根路徑到 HTMX 版本
@htmx_bp.route('/')
def index():
    return render_template('HTMX_templates/login_interface.html')

# 主 HTMX 頁面
@htmx_bp.route('/login', methods=['POST'])
def login():

    return render_template('HTMX_templates/layout_with_chart.html')

@htmx_bp.route('/logout', methods=['POST'])
def logout():
    # 使用HTTP重定向而不是直接渲染模板
    return redirect('/htmx/')

# 獲取科目列表
@htmx_bp.route('/api/subjects')
def htmx_subjects():
    subjects = get_subjects()
    if request.headers.get('HX-Request') == 'true':
        # 如果是HTMX請求，返回HTML選項
        options_html = ""
        for subject in subjects:
            options_html += f'<option value="{subject}">{subject}</option>'
        
        # 添加"新增科目"選項
        options_html += '<option value="add-new">+ 新增科目</option>'
        return options_html
    else:
        # 如果是普通API請求，返回JSON
        return jsonify(subjects)

# 專門為JavaScript fetch請求提供的科目列表API
@htmx_bp.route('/api/subjects-list')
def htmx_subjects_list():
    """API端點：獲取所有科目（始終返回JSON格式）"""
    subjects = get_subjects()
    return jsonify(subjects)

# 獲取特定科目的講義列表
@htmx_bp.route('/api/lectures/<subject>')
def htmx_lectures(subject):
    """獲取指定科目的所有講義"""
    return jsonify(get_lectures(subject))

# 提供 data_server 目錄中的靜態文件
@htmx_bp.route('/data/<subject>/lectures/<filename>')
def serve_lecture_file(subject, filename):
    """提供講義相關文件的訪問"""
    file_path = os.path.join('app', 'data_server', subject, 'lectures', filename)
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return jsonify({'error': '文件不存在'}), 404

# 獲取特定科目的所有筆記
@htmx_bp.route('/api/notes/<subject>')
def notes(subject):
    """獲取指定科目的所有筆記"""
    #print('subject:', subject)
    return jsonify(get_notes(subject))

'''
# 獲取特定講義相關的所有筆記
@htmx_bp.route('/api/get_lecture_notes/<subject>/<lecture_id>', methods=['GET'])
def lecture_notes(subject, lecture_id):
    """獲取與特定講義相關的所有筆記"""
    return jsonify(get_notes_for_lecture(subject, lecture_id))
'''



# 章節大綱片段
@htmx_bp.route('/outline')
def outline_fragment():
    return render_template('HTMX_templates/outline.html')

# 獲取特定科目講義的樹狀結構圖
@htmx_bp.route('/outline/get_tree_images/<subject>/<lecture_name>')
def htmx_subject_lecture_tree_images(subject, lecture_name):
    """API端點：獲取指定講義的樹狀結構圖片"""
    # 檢查科目是否存在
    subjects = get_subjects()
    if subject not in subjects:
        return jsonify({'error': '科目不存在'}), 404
    
    if not lecture_name:
        return jsonify({'error': '未提供講義名稱'}), 400
    
    # 返回圖片路徑列表
    images = []
    
    # 檢查講義對應的樹狀圖是否存在
    lecture_name_without_extension = os.path.splitext(lecture_name)[0]
    tree_image_filename = f"{lecture_name_without_extension}_tree.png"
    file_path = os.path.join('app', 'data_server', subject, 'lectures', tree_image_filename)

    if os.path.exists(file_path):
        url_path = f'/htmx/data/{subject}/lectures/{tree_image_filename}'
        images.append(url_path)

    return jsonify({
        'success': True,
        'images': images,
        'lecture_name': lecture_name
    })

# 重點統合片段
@htmx_bp.route('/integration')
def integration_fragment():
    """重點統合頁面片段"""
    return render_template('HTMX_templates/integration.html') 

# 獲取指定講義的頁數信息
@htmx_bp.route('/integration/get_num_pages/<subject>/<lecture_name>')
def integration_get_num_pages(subject, lecture_name):
    """API端點：獲取指定講義的頁數信息"""

    # 獲取講義的頁數
    file_path = os.path.join('app', 'data_upload', subject, 'lectures', lecture_name)
    print('file_path:', file_path)
    num_pages = get_num_pages(file_path)
    return jsonify({
        'success': True,
        'total_pages': num_pages
    }) 

@htmx_bp.route('/integration/get_page_info/<subject>/<lecture_name>/<page_num>')
def integration_get_page_info(subject, lecture_name, page_num):
    """API端點：獲取指定講義特定頁的預覽圖"""

    data = processing_get_page_info(subject, lecture_name, int(page_num)-1)
    return jsonify({
        'success': True,
        'data': data
    })

# 重點列表片段
@htmx_bp.route('/key_points')
def key_points_fragment():
    # 渲染模板而不需要傳遞數據，數據將由JavaScript動態加載
    return render_template('HTMX_templates/key_points.html')

# 獲取特定科目的重點列表
@htmx_bp.route('/key_points/get_keypoints/<subject>/<lecture_name>')
def htmx_subject_key_points(subject, lecture_name):
    """API端點：獲取指定科目的重點列表"""
    # 檢查科目是否存在
    subjects = get_subjects()
    if subject not in subjects:
        return jsonify({'error': '科目不存在'}), 404
        
    keypoints = processing_get_keypoints(subject, lecture_name)
    
    return jsonify({
        'success': True,
        'key_points': keypoints
    })

# 筆記列表片段
@htmx_bp.route('/notes')
def notes_fragment():
    # 渲染模板而不需要傳遞數據，數據將由JavaScript動態加載
    return render_template('HTMX_templates/notes.html')

@htmx_bp.route('/notes/get_notes/<subject>/<note_name>')
def notes_get_notes(subject, note_name):
    """API端點：獲取指定科目的所有筆記詳細資訊"""
    # 檢查科目是否存在
    subjects = get_subjects()
    if subject not in subjects:
        return jsonify({'success': False, 'error': '科目不存在'}), 404
    
    try:    
        notes = processing_get_notes(subject, note_name)
        #print(f"獲取到的筆記數據: {notes}")  # 添加日誌輸出以查看數據結構
        
        return jsonify({
            'success': True,
            'notes': notes
        })
    except Exception as e:
        #print(f"處理筆記時發生錯誤: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# 測驗系統片段
@htmx_bp.route('/quiz')
def quiz_fragment():
    return render_template('HTMX_templates/quiz.html')


# 產生測驗題目
@htmx_bp.route('/quiz/generate/<subject>/<lecture_name>/<num_questions>')
def generate_quiz(subject, lecture_name, num_questions):
    """API端點：獲取指定科目的測驗題目"""

    if not lecture_name:
        return jsonify({'success': False, 'error': '缺少講義名稱參數'}), 400
    
    try:
        # 調用處理函數獲取測驗題目
        quizzes = processing_get_questions(subject, lecture_name, int(num_questions))
        
        return jsonify({
            'success': True,
            'quizzes': quizzes
        })
    except Exception as e:
        print('error:', e)
        return jsonify({'success': False, 'error': str(e)}), 500

# 更新權重
@htmx_bp.route('/quiz/post_result/<subject>/<lecture_name>', methods=['POST'])
def post_result(subject, lecture_name):
    """更新後端評分紀錄"""
    
    # 獲取JSON數據(result 應為一個陣列，每個元素包含Keypoint_index與答對與否)
    answer_results = request.get_json()
    #print(f"接收到的答題結果數據: {answer_results}")
    
    try:
        processing_update_weights(subject, lecture_name, answer_results)
        processing_update_topics(subject, lecture_name, answer_results)
        return jsonify({'success': True})
    except Exception as e:
        print(f"處理答題結果出錯: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# 上傳檔案片段
@htmx_bp.route('/upload_lecture')
def upload_fragment():
    return render_template('HTMX_templates/upload_lecture.html')

# 上傳筆記片段
@htmx_bp.route('/upload_note')
def upload_note_fragment():
    return render_template('HTMX_templates/upload_note.html')


# 學習紀錄片段
@htmx_bp.route('/history')
def history_fragment():
    return render_template('HTMX_templates/history.html')

@htmx_bp.route('/history/get_history/<subject>/<lecture_name>')
def get_history(subject, lecture_name):
    """API端點：獲取指定科目的學習率"""
    
    try:
        history = processing_get_history(subject, lecture_name)
        # print('history:', history)
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        print('error:', e)
        return jsonify({'success': False, 'error': str(e)}), 500

@htmx_bp.route('/subjects/create', methods=['POST'])
def htmx_create_subject():
    """API端點：創建新科目"""
    data = request.get_json()
    
    if not data or 'subject_name' not in data:
        return jsonify({'success': False, 'error': '缺少科目名稱參數'}), 400
    
    subject_name = data['subject_name']
    
    # 驗證科目名稱
    if not subject_name or len(subject_name.strip()) == 0:
        return jsonify({'success': False, 'error': '科目名稱不能為空'}), 400
    
    # 創建科目資料夾結構
    result = create_subject_folders(subject_name)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@htmx_bp.route('/subjects/delete', methods=['POST'])
def htmx_delete_subject():
    """API端點：刪除科目"""
    data = request.get_json()
    
    if not data or 'subject_name' not in data:
        return jsonify({'success': False, 'error': '缺少科目名稱參數'}), 400
    
    subject_name = data['subject_name']
    
    # 驗證科目名稱
    if not subject_name or len(subject_name.strip()) == 0:
        return jsonify({'success': False, 'error': '科目名稱不能為空'}), 400
    
    # 檢查科目名稱是否存在
    subjects = get_subjects()
    if subject_name not in subjects:
        return jsonify({'success': False, 'error': '該科目不存在'}), 404
    
    # 刪除科目資料夾
    result = delete_subject_folders(subject_name)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 500

