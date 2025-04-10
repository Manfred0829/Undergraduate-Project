import requests
import json
from io import BytesIO

from app.modules.module_template import LazySingleton

class OCRspaceRequest(LazySingleton):
    OCRSPACE_API_TOKEN = None

    def initialize(self):
        """初始化方法"""
        import config 

        # 獲取 Api key
        self.OCRSPACE_API_TOKEN = config.get_env_variable("OCRSPACE_API_TOKEN")

        # 設定已初始化
        self._initialized = True


    def generate_img_OCR(self, image, overlay=True, language='eng', OCREngine=1, filename='image.jpg'):
        """
        OCR.space API request with an in-memory image object (e.g., from PIL or OpenCV).
        :param image: A PIL Image object or numpy array (already decoded image).
        :param overlay: Whether overlay is required in response.
        :param api_key: Your OCR.space API key.
        :param language: Language code (e.g., 'eng', 'chs').
        :param OCREngine: Engine number (1 or 2).
        :param filename: The filename to send to API (can be anything with proper extension).
        :return: Result in JSON string.
        """
        # 將圖片轉為 BytesIO 格式
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='JPEG')  # 可以改成 'PNG' 根據你的圖片格式
        img_byte_arr.seek(0)

        payload = {
            'isOverlayRequired': overlay,
            'apikey': self.OCRSPACE_API_TOKEN,
            'language': language,
            'OCREngine': OCREngine,
        }

        files = {
            'filename': (filename, img_byte_arr, 'image/jpeg')
        }

        r = requests.post('https://api.ocr.space/parse/image',
                        files=files,
                        data=payload)
        
        return r.content.decode()
    
    def _merge_words_to_pages(self, OCR_results):
        pages_list = []
        for page in OCR_results:
            page_content = ""
            for line in page:
                page_content += "" + line["LineText"] + "\n"
            
            pages_list.append(page_content)

        return pages_list
    
    def processing_handouts_OCR(self, img_list, language='eng'):
        OCR_results = []

        for img in img_list:
            OCR_result_str = self.generate_img_OCR(img)
            OCR_result_json = json.loads(OCR_result_str)
            page_lines = OCR_result_json['ParsedResults'][0]['TextOverlay']['Lines']
            OCR_results.append(page_lines)

        pages_list = self._merge_words_to_pages(OCR_results)
        return pages_list
