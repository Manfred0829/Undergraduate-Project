from app.utils import media_processer as media, text_processer as text, similarity_calculator as sim
from app.modules.models_request.OCRspace_request import OCRspaceRequest
from app.modules.models_local.EasyOCR_local import EasyOCRLocal
from app.modules.models_request.OpenAI_request import OpenAIRequest
from app.modules.questioning_manager import QuestioningManager
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

def processing_note(subject, lecture_name, img_path):
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

            # 如果筆記觀念錯誤則將Content替換成更正後，並另外保留原始內容
            if result['isCorrected']:
                note['Wrong_Content'] = note['Content']
                note['Content'] = result['Corrected_Content']
        logger.info("重點觀念修正完成")


        # embedding process
        texts_for_embedding = [nt["Title"] + ":\n" + nt["Content"] for nt in notes_json]
        vectors = OpenAI.processing_embedding(texts_for_embedding)
        for i in range(len(vectors)):
            notes_json[i]['Embedding'] = vectors[i]
        logger.info("嵌入向量處理完成")


        # simularity process
        lecturename_without_ext = os.path.splitext(lecture_name)[0]
        keypoints_path = os.path.join("app", "data_server", subject, "lectures", lecturename_without_ext, "_keypoints.json") # 讀取keypoints資料
        keypoints_json = text.read_json(keypoints_path)
        keypoints_embedding = [k["Embedding"] for k in keypoints_json]

        for n_idx, note in enumerate(notes_json):
            # 筆記json中儲存k_idx
            k_idx = sim.get_most_similar_index(note["Embedding"],keypoints_embedding)
            note["Keypoint_Index"] = k_idx

            # 講義json中儲存n_idx
            note_info = {"Notes_File_Name":original_filename , "Note_Index":n_idx}
            if "Notes" not in keypoints_json[k_idx]: # 第一次加入筆記
                keypoints_json[k_idx]["Notes"] = [note_info]
            else:
                keypoints_json[k_idx]["Notes"].append(note_info)

            if note['isCorrected']: # 筆記錯誤
                keypoints_json[k_idx]['Learning_Progress'] -= 1
            else: # 筆記正確
                keypoints_json[k_idx]['Learning_Progress'] += 1
        
        text.write_json(keypoints_json,keypoints_path) # 儲存更新後的keypoints資料
        logger.info("相似度對應處理完成")
        
        # save
        notes_save = {"Lecture_Name": lecture_name, "Notes": notes_json}
        output_path = os.path.join(notes_output_dir, f"{filename_without_ext}.json")
        text.write_json(notes_save, output_path)

        
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

        # 確保至少有一個主題
        if not topics_json:
            logger.warning("沒有找到任何主題，將建立預設主題")
            topics_json = [{
                "Topic": "預設主題",
                "Starting_page": 1
            }]

        # 為每個主題關聯相應的頁面
        for i, topic in enumerate(topics_json):
            start_page = max(0, topic['Starting_page'] - 1)  # 確保索引至少為0
            end_page = topics_json[i + 1]['Starting_page'] - 1 if i + 1 < len(topics_json) else len(pages_json)
            # 加入 'Pages' 欄位，內含 pages_json 中對應的每一頁資料
            topic['Pages'] = pages_json[start_page:end_page]

        # extract sections process
        sections_json = OpenAI.processing_handouts_extract_section([topic['Topic'] for topic in topics_json])
        logger.info(f"已提取 {len(sections_json)} 個章節")

        # 確保至少有一個段落
        if not sections_json:
            logger.warning("沒有找到任何段落，將建立預設段落")
            sections_json = [{
                "Section": "預設段落",
                "Starting_topic": 1
            }]

        # 為每個段落關聯相應的主題
        for i, section in enumerate(sections_json):
            start_topic = max(0, section['Starting_topic'] - 1)  # 確保索引至少為0
            end_topic = sections_json[i + 1]['Starting_topic'] - 1 if i + 1 < len(sections_json) else len(topics_json)
            # 加入 'Topics' 欄位，內含 topics_json 中對應的每一頁資料
            section['Topics'] = topics_json[start_topic:end_topic]

        # extract chapter process
        try:
            # 嘗試獲取第一頁的文本用於提取章節信息
            first_page_text = ""
            if sections_json and sections_json[0].get('Topics') and sections_json[0]['Topics'] and \
               sections_json[0]['Topics'][0].get('Pages') and sections_json[0]['Topics'][0]['Pages'] and \
               sections_json[0]['Topics'][0]['Pages'][0].get('Original_text'):
                first_page_text = sections_json[0]['Topics'][0]['Pages'][0]['Original_text']
            else:
                # 如果無法通過預期路徑獲取，則嘗試從 pages_json 獲取第一頁文本
                if pages_json and pages_json[0].get('Original_text'):
                    first_page_text = pages_json[0]['Original_text']
                    logger.warning("無法從章節層次獲取第一頁文本，使用直接的第一頁文本代替")
            
            # 生成章節信息
            chapter_json = OpenAI.processing_handouts_extract_chapter(filename_without_ext, first_page_text)
            logger.info("已提取章節信息")

        except Exception as e:
            # 如果提取章節過程中出錯，建立默認章節信息
            logger.warning(f"提取章節信息時發生錯誤: {e}，使用默認章節信息")
            chapter_json = {"Chapter": filename_without_ext or "未命名章節"}

        # 將章節和段落信息關聯起來
        chapter_json['Sections'] = sections_json

        # 確保目標目錄存在
        path = os.path.join(lectures_output_dir, filename_without_ext + ".json")
        text.write_json(chapter_json, path)
        logger.info(f"講義結構已保存到: {path}")

        # embedding process
        keypoints_list = _extract_keypoints_hierarchy(chapter_json)
        
        # 確保每個關鍵點有有效的標題和內容
        for kp in keypoints_list:
            if not kp.get("Title"):
                kp["Title"] = "未定義標題"
            if not kp.get("Content"):
                kp["Content"] = "未定義內容"
        
        # 格式化關鍵點用於嵌入
        keypoints_flatten = [kp["Title"] + ":\n" + kp["Content"] for kp in keypoints_list]
        
        # 檢查是否存在關鍵點
        if not keypoints_flatten:
            logger.warning("沒有找到任何關鍵點，將使用預設值")
            keypoints_flatten = ["本文件沒有提取到有效關鍵點"]
            # 創建一個具有預設值的關鍵點
            keypoints_list = [{
                "Title": "未定義標題",
                "Content": "本文件沒有提取到有效關鍵點",
                "Index": [0, 0, 0, 0],
                "from_page": 1
            }]
        
        vectors = OpenAI.processing_embedding(keypoints_flatten)
        
        # 確保向量和關鍵點列表長度匹配
        if len(vectors) != len(keypoints_list):
            logger.warning(f"向量數量({len(vectors)})與關鍵點數量({len(keypoints_list)})不匹配")
            # 如果向量少於關鍵點，補充零向量
            while len(vectors) < len(keypoints_list):
                vectors.append([0.0] * 1536)  # text-embedding-3-small的向量維度是1536
            # 如果向量多於關鍵點，截斷向量
            vectors = vectors[:len(keypoints_list)]

        # generate difficulity, importance process
        weights = OpenAI.processing_handouts_weights(subject, keypoints_flatten)

        # 加入info
        for i, kp in enumerate(keypoints_list):
            kp["Embedding"] = vectors[i]
            kp["Difficulty"] = weights[i]["Difficulty"]
            kp["Importance"] = weights[i]["Importance"]
            kp["Learning_Progress"] = 0

        # save
        keypoints_path = os.path.join(lectures_output_dir, filename_without_ext + "_keypoints.json")
        text.write_json(keypoints_list, keypoints_path)
        logger.info(f"重點嵌入向量已保存到: {keypoints_path}")
        
        # tree diagram process
        tree_path = os.path.join(lectures_output_dir, filename_without_ext + "_tree")
        tree_img_path = tree_path + ".png"
        try:
            media.generate_chapter_hierarchy_graph(chapter_json, tree_path)
            logger.info(f"樹狀結構圖已生成並保存到: {tree_img_path}")
        except Exception as e:
            logger.error(f"生成樹狀結構圖時出錯: {e}")
            # 確保即使圖無法生成，整個過程也能繼續
        
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

        if not chapter or not isinstance(chapter, dict):
            logger.error("章節資料無效或為空")
            return keypoints_list

        sections = chapter.get('Sections', [])
        if not sections:
            logger.warning("章節中沒有找到任何段落")
            return keypoints_list

        for s_idx, section in enumerate(sections):
            if not section or not isinstance(section, dict):
                logger.warning(f"第 {s_idx+1} 個段落資料無效，已跳過")
                continue

            topics = section.get('Topics', [])
            if not topics:
                logger.warning(f"第 {s_idx+1} 個段落中沒有找到任何主題")
                continue

            for t_idx, topic in enumerate(topics):
                if not topic or not isinstance(topic, dict):
                    logger.warning(f"第 {s_idx+1} 段落中第 {t_idx+1} 個主題資料無效，已跳過")
                    continue

                pages = topic.get('Pages', [])
                if not pages:
                    logger.warning(f"第 {s_idx+1} 段落的第 {t_idx+1} 個主題中沒有找到任何頁面")
                    continue

                for p_idx, page in enumerate(pages):
                    if not page or not isinstance(page, dict):
                        logger.warning(f"第 {s_idx+1} 段落第 {t_idx+1} 主題中第 {p_idx+1} 頁資料無效，已跳過")
                        continue

                    keypoints = page.get('Keypoints', [])
                    if not keypoints:
                        # 這是正常的，因為不是每個頁面都有關鍵點
                        continue

                    page_idx = page.get("page_idx", p_idx + 1)

                    for k_idx, k in enumerate(keypoints):
                        if not k or not isinstance(k, dict):
                            logger.warning(f"在第 {page_idx} 頁中找到無效關鍵點，已跳過")
                            continue

                        keypoint = {
                            "Title": k.get("Title", "").strip(),
                            "Content": k.get("Content", "").strip(),
                            "Index": [s_idx, t_idx, p_idx, k_idx],
                            "from_page": page_idx
                        }

                        # 只添加有內容的關鍵點
                        if keypoint["Title"] or keypoint["Content"]:
                            keypoints_list.append(keypoint)

        logger.info(f"已從章節結構中提取 {len(keypoints_list)} 個重點")
        return keypoints_list
        
    except Exception as e:
        logger.error(f"提取重點層次結構時發生錯誤: {str(e)}", exc_info=True)
        return []


def processing_get_keypoints(subject, lecture_name):
    # 讀取 json
    lecturename_without_ext = os.path.splitext(lecture_name)[0]
    keypoints_path = os.path.join("app", "data_server", subject, "lectures", lecturename_without_ext + "_keypoints.json")
    # print(keypoints_path)
    keypoints_json = text.read_json(keypoints_path, default_content=[])

    for keypoint in keypoints_json:
        # 刪除不需要的欄位（安全 pop）
        for field in ["Index", "from_page", "Embedding"]:
            keypoint.pop(field, None)

        # 處理 Notes
        notes = keypoint.pop("Notes", None)
        if notes is not None:
            keypoint["Notes_count"] = len(notes)

        # 重命名進度欄位
        if "Learning_Progress" in keypoint:
            keypoint["Progress"] = keypoint.pop("Learning_Progress")

    return keypoints_json


def processing_get_questions(subject, lecture_name, num_questions):
    # 讀取 json
    lecturename_without_ext = os.path.splitext(lecture_name)[0]
    keypoints_path = os.path.join("app", "data_server", subject, "lectures", lecturename_without_ext + "_keypoints.json")
    keypoints_json = text.read_json(keypoints_path, default_content=[])

    if not keypoints_json:
        raise ValueError("無法讀取講義重點，請確認檔案是否存在且非空")
    
    QM = QuestioningManager(subject, keypoints_json)

    questions = []
    for i in range(num_questions):
        questions.append(QM.get_question())

    return questions


def processing_update_weights(subject, lecture_name, answer_results):
    # 讀取 json
    lecturename_without_ext = os.path.splitext(lecture_name)[0]
    keypoints_path = os.path.join("app", "data_server", subject, "lectures", lecturename_without_ext + "_keypoints.json")
    keypoints_json = text.read_json(keypoints_path, default_content=[])

    if not keypoints_json:
        raise ValueError("無法讀取講義重點，請確認檔案是否存在且非空")
    
    QM = QuestioningManager(subject, keypoints_json)

    edited_keypoints = QM.update_weights(answer_results)
    text.write_json(edited_keypoints, keypoints_path)

    return


def _get_notes_from_keypoint(subject, keypoint_json):
    result_notes = []
    for note in keypoint_json["Notes"]:
        notes_path = os.path.join("app", "data_server", subject, "notes", note["Notes_File_Name"])
        try:
            notes_json = text.read_json(notes_path)
            result_notes.append(notes_json[note["Note_Index"]])
        except Exception as e:
            print(f"Error reading notes file {notes_path}: {e}")
            continue  # 讀取錯誤則跳過此筆資料

    return result_notes  # 確保有返回結果


def processing_get_page_info(subject, lecture_name, page_index):
    # 1. page image
    pdf_path = os.path.join("app", "data_upload", subject, "lectures", lecture_name)
    imgs = media.read_pdf_to_images(pdf_path)
    result_img = imgs[page_index]
    # 將PIL圖像轉換為base64字串
    result_img_base64 = media.convert_PIL_to_base64(result_img)

    # 讀取 json
    lecturename_without_ext = os.path.splitext(lecture_name)[0]
    keypoints_path = os.path.join("app", "data_server", subject, "lectures", lecturename_without_ext + "_keypoints.json")
    keypoints_json = text.read_json(keypoints_path, default_content=[])
    target_keypoints = list(filter(lambda x: x["from_page"] == page_index, keypoints_json))

    # 2. keypoints
    result_keypoints = []
    for keypoint in target_keypoints:
        temp = {"Title": keypoint["Title"], "Content": keypoint["Content"]}
        result_keypoints.append(temp)

    # 3. notes
    result_notes = []
    for keypoint in target_keypoints:
        if "Notes" in keypoint:
            notes = _get_notes_from_keypoint(subject, keypoint)
            for note in notes:
                temp = {"Title": note["Title"], "Content": note["Content"]}
                result_notes.append(temp)

    result = {"Image": result_img_base64,
              "Keypoints": result_keypoints,
              "Notes": result_notes}
    return result

    