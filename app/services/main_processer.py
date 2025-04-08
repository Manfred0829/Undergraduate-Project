from app.utils import media_processer as media, text_processer as text
# from modules.models_request.OCRspace_request import OCRspaceRequest
from app.modules.models_local.EasyOCR_local import EasyOCRLocal
from app.modules.models_request.OpenAI_request import OpenAIRequest
import os


def processing_note(subject, img_path):

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

    # 從 img_path 中提取原始檔案名稱
    original_filename = os.path.basename(img_path)
    filename_without_ext = os.path.splitext(original_filename)[0]
    
    # 建立輸出路徑
    output_dir = os.path.join("app", "data_json", subject, "notes")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{filename_without_ext}.json")
    

    original_filename = os.path.basename(img_path)
    filename_without_ext = os.path.splitext(original_filename)[0]
    
    path = os.path.join("app", "data", subject, filename_without_ext + ".json")
    notes_db = text.read_json(path, default_content=[])
    notes_db.extend(notes_json)
    # 儲存合併後的結果到原始位置
    text.write_json(notes_db, path)

def processing_lecture(subject, img_path):
    pass

