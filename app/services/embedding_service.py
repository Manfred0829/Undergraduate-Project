# app/services/embedding_service.py
import os
import json
from app.services.file_service import (
    update_vector_embedding, ensure_data_directories,
    get_lecture, get_note
)

def process_embedding(file_type, file_id):
    """
    處理文件的向量嵌入
    
    Args:
        file_type: 'lecture' 或 'note'
        file_id: 文件ID
    
    Returns:
        dict: 處理結果
    """
    # 確保目錄存在
    dirs = ensure_data_directories()
    
    # 獲取文件數據
    if file_type == 'lecture':
        file_data = get_lecture(file_id)
    else:  # note
        file_data = get_note(file_id)
    
    if not file_data:
        return {'success': False, 'error': '找不到指定的文件'}
    
    # 檢查OCR是否已處理
    if not file_data.get('ocr_processed') or not file_data.get('ocr_text_path'):
        return {'success': False, 'error': '文件尚未經過OCR處理'}
    
    # 讀取OCR文本
    try:
        with open(file_data['ocr_text_path'], 'r', encoding='utf-8') as f:
            ocr_text = f.read()
    except Exception as e:
        return {'success': False, 'error': f'無法讀取OCR文本: {str(e)}'}
    
    # 創建向量嵌入存儲路徑
    subject = file_data['subject']
    vectors_subject_dir = os.path.join(dirs['vectors'], subject)
    if not os.path.exists(vectors_subject_dir):
        os.makedirs(vectors_subject_dir)
    
    vector_path = os.path.join(vectors_subject_dir, f"{file_id}.json")
    
    # 這裡應該調用實際的向量嵌入模型處理文本
    # 以下僅為示例，實際應用需替換為真實向量嵌入處理邏輯
    
    # 模擬向量嵌入結果 (這裡只是示例)
    embedding_result = {
        'file_id': file_id,
        'file_type': file_type,
        'vector': [0.1, 0.2, 0.3, 0.4, 0.5]  # 實際應用中這裡會是真實的向量表示
    }
    
    # 保存向量嵌入結果
    with open(vector_path, 'w', encoding='utf-8') as f:
        json.dump(embedding_result, f, ensure_ascii=False, indent=2)
    
    # 更新向量嵌入狀態和結果
    success = update_vector_embedding(file_type, file_id, vector_path)
    
    return {
        'success': success,
        'file_id': file_id,
        'vector_path': vector_path
    }

def compare_lecture_note(lecture_id, note_id):
    """
    比較講義和筆記的相似度，找到對應部分
    
    Args:
        lecture_id: 講義ID
        note_id: 筆記ID
    
    Returns:
        dict: 比較結果
    """
    # 獲取文件數據
    lecture = get_lecture(lecture_id)
    note = get_note(note_id)
    
    if not lecture or not note:
        return {'success': False, 'error': '找不到指定的講義或筆記'}
    
    # 檢查向量嵌入是否已處理
    if not lecture.get('vector_embeddings') or not note.get('vector_embeddings'):
        return {'success': False, 'error': '講義或筆記尚未經過向量嵌入處理'}
    
    # 讀取向量嵌入數據
    try:
        with open(lecture['vector_embeddings'], 'r', encoding='utf-8') as f:
            lecture_embedding = json.load(f)
        
        with open(note['vector_embeddings'], 'r', encoding='utf-8') as f:
            note_embedding = json.load(f)
    except Exception as e:
        return {'success': False, 'error': f'無法讀取向量嵌入數據: {str(e)}'}
    
    # 這裡應該實現實際的向量比較和匹配邏輯
    # 以下僅為示例，實際應用需替換為真實比較邏輯
    
    # 模擬比較結果 (這裡只是示例)
    comparison_result = {
        'lecture_id': lecture_id,
        'note_id': note_id,
        'similarity_score': 0.85,  # 實際應用中這裡會是真實的相似度分數
        'matching_sections': [
            {
                'lecture_section': '第一章 基礎概念',
                'note_section': '基礎概念摘要',
                'similarity': 0.92
            },
            {
                'lecture_section': '第二章 進階理論',
                'note_section': '理論應用筆記',
                'similarity': 0.78
            }
        ]
    }
    
    return {
        'success': True,
        'comparison': comparison_result
    }