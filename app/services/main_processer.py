from app.utils import media_processer as media, text_processer as text
from app.modules.models_request.OCRspace_request import OCRspaceRequest
from app.modules.models_local.EasyOCR_local import EasyOCRLocal
from app.modules.models_request.OpenAI_request import OpenAIRequest
import os


def processing_note(subject, img_path):

    # 從 img_path 中提取原始檔案名稱
    original_filename = os.path.basename(img_path)
    filename_without_ext = os.path.splitext(original_filename)[0]

    # Img process
    EasyOCR = EasyOCRLocal()
    img_PIL = media.read_image_to_PIL(img_path)
    cropped_images = EasyOCR.processing_lines_bounding_box(img_PIL,draw_result=True)

    # OCR process
    OpenAI = OpenAIRequest()

    page_texts = ""
    for cropped_img in cropped_images:
        base64_img = media.convert_PIL_to_base64(cropped_img)
        OCR_result_text = OpenAI.generate_img_OCR(base64_img)
        #print(OCR_result_text)
        page_texts += OCR_result_text + "\n"

    # LLM process
    repaired_page = OpenAI.processing_notes_repair(page_texts)
    notes_json = OpenAI.processing_notes_extract_keypoints(repaired_page)
    print(repaired_page)
    print(notes_json)

    # embedding process
    notes_embedding = OpenAI.processing_notes_embedding(notes_json)
    for i in range(len(notes_embedding)):
        notes_json[i]['Embedding'] = notes_embedding[i]

    # simularity process
    # temp mocking
    for note in notes_json:
        note['Keypoint_id'] = -1

    # 建立輸出路徑
    output_dir = os.path.join("app", "data_server", subject, "notes")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{filename_without_ext}.json")
    
    notes_db = text.read_json(output_path, default_content=[])
    notes_db.extend(notes_json)
    text.write_json(notes_db, output_path)



def processing_lecture(subject, pdf_path):

    original_filename = os.path.basename(pdf_path)
    filename_without_ext = os.path.splitext(original_filename)[0]

    # using default data
    OCR_result_list = text.read_json(pdf_path)

    
    pages_list = OCRspaceRequest.merge_words_to_pages(OCR_result_list)

    #test
    pages_list = pages_list[0:8]


    OpenAI = OpenAIRequest()

    # extract keypoints process
    pages_json = []
    for page_text in pages_list:
        page_json = {'Original_text': page_text}

        page_json['Keypoints'] = OpenAI.processing_handouts_extract_keypoints(page_text)

        page_json['Info'] = OpenAI.processing_handouts_page_info(page_text)
        pages_json.append(page_json)


    # extract topic process
    topics_json = OpenAI.processing_handouts_extract_topic([page_json['Info'] for page_json in pages_json])
    print(topics_json)

    for i, topic in enumerate(topics_json):
        start_page = topic['Starting_page'] -1
        end_page = topics_json[i + 1]['Starting_page'] -1 if i + 1 < len(topics_json) else len(pages_json)
    
        # 加入 'Pages' 欄位，內含 pages_json 中對應的每一頁資料
        topic['Pages'] = pages_json[start_page:end_page]


    # extract sections process
    sections_json = OpenAI.processing_handouts_extract_section([topic['Topic'] for topic in topics_json])
    print(sections_json)

    for i, section in enumerate(sections_json):
        start_topic = section['Starting_topic'] -1
        end_topic = sections_json[i + 1]['Starting_topic'] -1 if i + 1 < len(sections_json) else len(topics_json)
    
        # 加入 'Topics' 欄位，內含 topics_json 中對應的每一頁資料
        section['Topics'] = topics_json[start_topic:end_topic]

    
    # extract chapter process
    chapter_json = OpenAI.processing_handouts_extract_chapter(filename_without_ext,sections_json[0]['Topics'][0]['Pages'][0]['Original_text'])
    print(chapter_json)

    chapter_json['Sections'] = sections_json

    # save
    path = os.path.join("app", "data_server", subject, "lectures", filename_without_ext + ".json")
    text.write_json(chapter_json, path)


    # embedding process
    keypoints_list = _extract_keypoints_hierarchy(chapter_json)
    texts_for_embedding = [kp["Title"] + ":\n" + kp["Content"] for kp in keypoints_list]
    vectors = OpenAI.generate_embedding(texts_for_embedding)

    # 加入嵌入向量並移除文字欄位
    for i, kp in enumerate(keypoints_list):
        kp.pop("Title", None)
        kp.pop("Content", None)
        kp["Embedding"] = vectors[i]

    # save
    path = os.path.join("app", "data_server", subject, "lectures", filename_without_ext + "_keypoints.json")
    text.write_json(keypoints_list, path)

    # tree diagram process
    path = os.path.join("app", "data_server", subject, "lectures", filename_without_ext + "_tree.json")
    media.generate_chapter_hierarchy_graph(chapter_json,path)


def _extract_keypoints_hierarchy(chapter: dict):
    """
    從巢狀講義 JSON 檔中提取所有 keypoint，並標註其所屬的章節 / 主題 / 頁面索引。
    將結果儲存成新的 JSON 檔案。
    """

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
                        "Index": [s_idx, t_idx, p_idx, k_idx]
                    })

    print(f"✅ Keypoints with hierarchy generated")
    return keypoints_list

