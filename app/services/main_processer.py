from app.utils import media_processer as media, text_processer as text
from app.modules.models_request.OCRspace_request import OCRspaceRequest
from app.modules.models_local.EasyOCR_local import EasyOCRLocal
from app.modules.models_request.OpenAI_request import OpenAIRequest
import os
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ensure_directory_exists(directory_path):
    """確保目錄存在，如果不存在則創建它"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)
        logger.info(f"創建目錄: {directory_path}")

def processing_note(subject, img_path):
    """
    處理上傳的筆記圖片
    
    Args:
        subject: 科目名稱
        img_path: 圖片路徑
    
    Returns:
        dict: 處理結果
    """
    try:
        logger.info(f"開始處理筆記: {img_path}, 科目: {subject}")
        
        # 從 img_path 中提取原始檔案名稱
        original_filename = os.path.basename(img_path)
        filename_without_ext = os.path.splitext(original_filename)[0]

        # 確保目錄存在
        notes_output_dir = os.path.join("app", "data_server", subject, "notes")
        ensure_directory_exists(notes_output_dir)
        
        # Img process
        EasyOCR = EasyOCRLocal()
        img_PIL = media.read_image_to_PIL(img_path)
        if img_PIL is None:
            logger.error(f"無法讀取圖片: {img_path}")
            return {"success": False, "error": "無法讀取圖片檔案"}
        
        save_path = os.path.join("app", "data_server", subject, "notes", filename_without_ext + "_lines_bounding_box.png")
        cropped_images = EasyOCR.processing_lines_bounding_box(img_PIL, draw_result=True, save_path=save_path)
        logger.info(f"已處理圖片並分割成 {len(cropped_images)} 個文字區域")

        # OCR process
        OpenAI = OpenAIRequest()

        page_texts = ""
        for cropped_img in cropped_images:
            base64_img = media.convert_PIL_to_base64(cropped_img)
            OCR_result_text = OpenAI.generate_img_OCR(base64_img)
            logger.info(f"OCR識別結果: {OCR_result_text[:30]}...")
            page_texts += OCR_result_text + "\n"

        # repair process
        repaired_page = OpenAI.processing_notes_repair(page_texts)
        logger.info("筆記修復完成")
        
        # extract process
        notes_json = OpenAI.processing_notes_extract_keypoints(repaired_page)
        logger.info("重點提取完成")

        # correct process
        for note in notes_json:
            result = OpenAI.processing_notes_correct(subject,note)
            note['isCorrected'] = result['isCorrected']

            if result['isCorrected']:
                note['Wrong_Content'] = note['Content']
                note['Content'] = result['Corrected_Content']
        logger.info("重點觀念修正完成")


        # embedding process
        texts_for_embedding = [nt["Title"] + ":\n" + nt["Content"] for nt in notes_json]
        vectors = OpenAI.generate_embedding(texts_for_embedding)
        for i in range(len(vectors)):
            notes_json[i]['Embedding'] = vectors[i]
        logger.info("嵌入向量處理完成")

        # simularity process
        # temp mocking
        for note in notes_json:
            note['Keypoint_id'] = -1

        # 建立輸出路徑
        output_path = os.path.join(notes_output_dir, f"{filename_without_ext}.json")
        
        # 讀取現有資料或建立新檔案
        notes_db = text.read_json(output_path, default_content=[])
        notes_db.extend(notes_json)
        text.write_json(notes_db, output_path)
        
        logger.info(f"筆記處理完成，已保存到: {output_path}")
        return {"success": True, "message": "筆記處理完成", "output_path": output_path}
        
    except Exception as e:
        logger.error(f"處理筆記時發生錯誤: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}


def processing_lecture(subject, pdf_path):
    """
    處理上傳的講義PDF
    
    Args:
        subject: 科目名稱
        pdf_path: PDF路徑
    
    Returns:
        dict: 處理結果
    """
    try:
        logger.info(f"開始處理講義: {pdf_path}, 科目: {subject}")
        
        original_filename = os.path.basename(pdf_path)
        filename_without_ext = os.path.splitext(original_filename)[0]
        
        # 確保目錄存在
        lectures_output_dir = os.path.join("app", "data_server", subject, "lectures")
        ensure_directory_exists(lectures_output_dir)

        # 僅用於測試 - 處理前8頁
        #OCR_result_list = text.read_json(pdf_path)
        #pages_list = pages_list[0:min(8, len(pages_list))]

        # OCR procrss
        img_list = media.read_pdf_to_images(pdf_path)
        if not img_list or len(img_list) == 0:
            logger.error(f"無法讀取PDF: {pdf_path}")
            return {"success": False, "error": "無法讀取PDF檔案"}
            
        OCRspace = OCRspaceRequest()
        
        # 限制處理頁數，防止API成本過高 (測試用)
        max_pages = min(8, len(img_list))
        pages_list = OCRspace.processing_handouts_OCR(img_list[0:max_pages])
        logger.info(f"OCR識別完成，共處理 {len(pages_list)} 頁")
    
        # extract keypoints process
        OpenAI = OpenAIRequest()

        pages_json = []
        for i, page_text in enumerate(pages_list):
            page_json = {'Original_text': page_text}
            page_json['Keypoints'] = OpenAI.processing_handouts_extract_keypoints(page_text)
            page_json['Info'] = OpenAI.processing_handouts_page_info(page_text)
            page_json['page_idx'] = i
            pages_json.append(page_json)

        logger.info(f"已處理 {len(pages_json)} 頁並提取重點")

        # extract topic process
        topics_json = OpenAI.processing_handouts_extract_topic([page_json['Info'] for page_json in pages_json])
        logger.info(f"已提取 {len(topics_json)} 個主題")

        for i, topic in enumerate(topics_json):
            start_page = topic['Starting_page'] - 1
            end_page = topics_json[i + 1]['Starting_page'] - 1 if i + 1 < len(topics_json) else len(pages_json)
            # 加入 'Pages' 欄位，內含 pages_json 中對應的每一頁資料
            topic['Pages'] = pages_json[start_page:end_page]

        # extract sections process
        sections_json = OpenAI.processing_handouts_extract_section([topic['Topic'] for topic in topics_json])
        logger.info(f"已提取 {len(sections_json)} 個章節")

        for i, section in enumerate(sections_json):
            start_topic = section['Starting_topic'] - 1
            end_topic = sections_json[i + 1]['Starting_topic'] - 1 if i + 1 < len(sections_json) else len(topics_json)
            # 加入 'Topics' 欄位，內含 topics_json 中對應的每一頁資料
            section['Topics'] = topics_json[start_topic:end_topic]

        # extract chapter process
        chapter_json = OpenAI.processing_handouts_extract_chapter(filename_without_ext,sections_json[0]['Topics'][0]['Pages'][0]['Original_text'])
        logger.info("已提取章節信息")

        chapter_json['Sections'] = sections_json

        # 確保目標目錄存在
        path = os.path.join(lectures_output_dir, filename_without_ext + ".json")
        text.write_json(chapter_json, path)
        logger.info(f"講義結構已保存到: {path}")

        # embedding process
        keypoints_list = _extract_keypoints_hierarchy(chapter_json)
        keypoints_flatten = [kp["Title"] + ":\n" + kp["Content"] for kp in keypoints_list]
        vectors = OpenAI.generate_embedding(keypoints_flatten)

        # generate difficulity, importance process
        weights = OpenAI.processing_handouts_weights(subject, keypoints_flatten)

        # 加入info
        for i, kp in enumerate(keypoints_list):
            kp["Embedding"] = vectors[i]
            kp["Difficulty"] = weights[i]["Difficulty"]
            kp["Importance"] = weights[i]["Importance"]

        # save
        keypoints_path = os.path.join(lectures_output_dir, filename_without_ext + "_keypoints.json")
        text.write_json(keypoints_list, keypoints_path)
        logger.info(f"重點嵌入向量已保存到: {keypoints_path}")
        
        # tree diagram process
        tree_path = os.path.join(lectures_output_dir, filename_without_ext + "_tree.json")
        media.generate_chapter_hierarchy_graph(chapter_json, tree_path)
        
        return {
            "success": True, 
            "message": "講義處理完成", 
            "output_path": path, 
            "keypoints_path": keypoints_path,
            "tree_path": tree_path
        }
        
    except Exception as e:
        logger.error(f"處理講義時發生錯誤: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}


def _extract_keypoints_hierarchy(chapter: dict):
    """
    從巢狀講義 JSON 檔中提取所有 keypoint，並標註其所屬的章節 / 主題 / 頁面索引。
    將結果儲存成新的 JSON 檔案。
    """
    try:
        keypoints_list = []

        sections = chapter.get('Sections', [])
        for s_idx, section in enumerate(sections):
            topics = section.get('Topics', [])
            for t_idx, topic in enumerate(topics):
                pages = topic.get('Pages', [])
                for p_idx, page in enumerate(pages):
                    keypoints = page.get('Keypoints', [])
                    for k_idx, k in enumerate(keypoints):
                        keypoints_list.append({
                            "Title": k.get("Title", ""),
                            "Content": k.get("Content", ""),
                            "Index": [s_idx, t_idx, p_idx, k_idx],
                            "from_page": page["page_idx"]
                        })

        logger.info(f"已從章節結構中提取 {len(keypoints_list)} 個重點")
        return keypoints_list
        
    except Exception as e:
        logger.error(f"提取重點層次結構時發生錯誤: {str(e)}", exc_info=True)
        return []

