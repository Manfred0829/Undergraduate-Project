import concurrent.futures
import time
import json
import requests

from app.modules.module_template import LazySingleton

class OCRspaceRequest(LazySingleton):
    model = None
    genai = None
    OCRSPACE_API_TOKEN = None

    def initialize(self):
        """初始化方法"""
        from app import config 

        # 獲取 Api key
        self.OCRSPACE_API_TOKEN = config.get_env_variable("OCRSPACE_API_TOKEN")

        # 設定已初始化
        self._initialized = True


    def generate_img_OCR(self, img_path):
    
        raise NotImplementedError("Using default Data, didn't implemented OCR process.")

    
    def merge_words_to_pages(OCR_result):
        page_list = []
        for page in OCR_result:
            page_content = ""
            for line in page:
                page_content += "" + line["LineText"] + "\n"
            
            page_list.append(page_content)

        return page_list