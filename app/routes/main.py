from flask import Blueprint, render_template, jsonify, request
from app.services.file_service import get_subjects, get_lectures, get_notes, create_subject_folders, delete_subject_folders
from app.services.main_processer import processing_get_keypoints, processing_get_page_info, processing_get_questions
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

@main_bp.route('/api/subjects/create', methods=['POST'])
def create_subject():
    """API端點：創建新科目"""
    data = request.get_json()
    
    if not data or 'subject_name' not in data:
        return jsonify({'success': False, 'error': '缺少科目名稱參數'}), 400
    
    subject_name = data['subject_name']
    
    # 驗證科目名稱
    if not subject_name or len(subject_name.strip()) == 0:
        return jsonify({'success': False, 'error': '科目名稱不能為空'}), 400
    
    # 檢查科目名稱是否已存在
    subjects = get_subjects()
    if subject_name in subjects:
        return jsonify({'success': False, 'error': '該科目已存在'}), 400
    
    # 創建科目資料夾
    result = create_subject_folders(subject_name)
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 500

@main_bp.route('/api/subjects/delete', methods=['POST'])
def delete_subject():
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

@main_bp.route('/api/subjects/<subject>/outline')
def subject_outline(subject):
    """API端點：獲取指定科目的學習大綱"""
    # 目前返回空內容，實際應該從資料庫或檔案中讀取大綱
    # 如果該科目沒有大綱，返回404
    
    # 檢查科目是否存在
    subjects = get_subjects()
    if subject not in subjects:
        return jsonify({'error': '科目不存在'}), 404
        
    # 這裡只是返回一個空的大綱結構
    # 實際應用中，應該從資料庫或檔案中讀取該科目的大綱
    return jsonify({
        'success': True,
        'outline': []
    })

@main_bp.route('/api/subjects/<subject>/quizzes')
def subject_quizzes(subject):
    """API端點：獲取指定科目的測驗題目"""
    # 檢查科目是否存在
    subjects = get_subjects()
    if subject not in subjects:
        return jsonify({'error': '科目不存在'}), 404
    
    # 從請求中獲取講義名稱和題目數量
    lecture_name = request.args.get('lecture_name')
    num_questions = request.args.get('num_questions', 5, type=int)
    
    if not lecture_name:
        return jsonify({'success': False, 'error': '缺少講義名稱參數'}), 400
    
    try:
        # 調用處理函數獲取測驗題目
        quizzes = processing_get_questions(subject, lecture_name, num_questions)
        
        return jsonify({
            'success': True,
            'quizzes': quizzes
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/subjects/<subject>/lecture_tree_images')
def subject_lecture_tree_images(subject):
    """API端點：獲取指定科目的講義樹狀結構圖"""
    import os
    from flask import current_app
    
    # 檢查科目是否存在
    subjects = get_subjects()
    if subject not in subjects:
        return jsonify({'error': '科目不存在'}), 404
    
    # 查找該科目下所有以tree.json.png結尾的文件
    tree_images = []
    lectures_dir = os.path.join(current_app.config['DATA_SERVER_DIR'], subject, 'lectures')
    
    if os.path.exists(lectures_dir):
        for file in os.listdir(lectures_dir):
            if file.endswith('tree.json.png'):
                # 生成文件的URL路徑
                image_path = f'/data_server/{subject}/lectures/{file}'
                tree_images.append(image_path)
    
    # 按文件名排序（通常包含數字，如w1, w2等）
    tree_images.sort()
    
    return jsonify({
        'success': True,
        'images': tree_images
    })

@main_bp.route('/api/subjects/<subject>/key_points')
def subject_key_points(subject):
    """API端點：獲取指定科目的重點列表"""
    # 檢查科目是否存在
    subjects = get_subjects()
    if subject not in subjects:
        return jsonify({'error': '科目不存在'}), 404
        
    # 這裡只是返回一個空的重點列表結構
    # 實際應用中，應該從資料庫或檔案中讀取該科目的重點列表
    lecture_name = request.args.get('lecture_name')
    keypoints = processing_get_keypoints(subject, lecture_name)
    # print(keypoints)
    return jsonify({
        'success': True,
        'key_points': keypoints
    })

@main_bp.route('/api/subjects/<subject>/integration')
def lecture_integration(subject):
    """API端點：獲取指定講義特定頁的預覽圖"""
    # 這個函數會返回講義特定頁的預覽圖
    # 實際應用中，應該從資料庫或檔案系統中獲取預覽圖
    # 這裡只返回一個空響應
    subjects = get_subjects()
    if subject not in subjects:
        return jsonify({'error': '科目不存在'}), 404
    
    lecture_name = request.args.get('lecture_name')
    page_num = request.args.get('page_num')
    data = processing_get_page_info(subject, lecture_name, int(page_num))
    return jsonify({
        'success': True,
        'data': data
    })

# @main_bp.route('/api/lectures/<lecture_id>/integration/<page_num>')
# def lecture_integration(lecture_id, page_num):
#     """API端點：獲取指定講義特定頁的重點統合數據"""
#     # 這個函數會返回講義特定頁的重點統合數據，包括講義重點和筆記重點
#     # 實際應用中，應該從資料庫或檔案系統中獲取重點統合數據
#     # 這裡只返回一個空響應
    
#     lecture_name = request.args.get('lecture_name')
#     data = processing_get_page_info(subject, lecture_name, page_num)
#     return jsonify({
#         'success': True,
#         'lecture_points': [],
#         'note_points': []
#     })

@main_bp.route('/api/lectures/<lecture_id>/pages')
def lecture_pages(lecture_id):
    """API端點：獲取指定講義的頁數信息"""
    # 這個函數會返回講義的頁數信息
    # 實際應用中，應該從資料庫或檔案系統中獲取頁數信息
    # 這裡只返回一個示例響應
    return jsonify({
        'success': True,
        'total_pages': 10  # 假設有10頁
    }) 