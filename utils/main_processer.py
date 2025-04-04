from utils import media_processer as media, text_processer as text
# from modules.models_request.OCRspace_request import OCRspaceRequest
from modules.models_local.EasyOCR_local import EasyOCRLocal
from modules.models_request.OpenAI_request import OpenAIRequest



def processing_note(img_path):

    # Img process
    EasyOCR = EasyOCRLocal()
    img_PIL = media.read_image_to_PIL(img_path)
    cropped_images = EasyOCR.processing_lines_bounding_box(img_PIL,draw_result=False)

    # OCR process
    OpenAI = OpenAIRequest()

    page_texts = ""
    for cropped_img in cropped_images:
        base64_img = media.convert_PIL_to_base64(cropped_img)
        OCR_result_text = OpenAI.generate_img_OCR(base64_img)
        #print(OCR_result_text)
        page_texts += OCR_result_text + "\n"

    print(page_texts)