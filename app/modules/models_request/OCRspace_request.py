import requests
import json
from io import BytesIO
from PIL import Image
import config 
from app.modules.module_template import LazySingleton

class OCRspaceRequest(LazySingleton):
    OCRSPACE_API_TOKEN = None

    def initialize(self):
        """初始化方法"""

        # 獲取 Api key
        TOKEN_NUM = int(config.get_env_variable("OCRSPACE_API_TOKEN_NUM"))
        self.TOKEN_LIST = [config.get_env_variable(f"OCRSPACE_API_TOKEN_{i}") for i in range(1, TOKEN_NUM + 1)]
        self.TOKEN_INDEX = 0
        self.TOKEN_NUM = TOKEN_NUM

        # 設定已初始化
        self._initialized = True

    

    def _check_and_compress_image(self, image, max_size_mb=1, p_idx=-1):
        """
        檢查圖片大小並在需要時進行壓縮
        :param image: PIL Image 物件
        :param max_size_mb: 最大允許的圖片大小 (MB)
        :return: 壓縮後的 PIL Image 物件
        """
        # 轉為 BytesIO 檢查大小
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        # 計算大小 (MB)
        size_mb = len(img_byte_arr.getvalue()) / (1024 * 1024)
        
        # 如果大小超過限制，進行壓縮
        if size_mb > max_size_mb:
            print(f"The page {p_idx+1} is too large.")
            print("==> Compressing the image...")
            # 計算壓縮比例
            compression_ratio = (max_size_mb / size_mb) ** 0.5
            new_width = int(image.width * compression_ratio)
            new_height = int(image.height * compression_ratio)
            
            # 調整圖片大小
            compressed_image = image.resize((new_width, new_height), Image.LANCZOS)
            
            # 再次檢查大小
            img_byte_arr = BytesIO()
            compressed_image.save(img_byte_arr, format='JPEG', quality=85)
            img_byte_arr.seek(0)
            
            new_size_mb = len(img_byte_arr.getvalue()) / (1024 * 1024)
            
            # 如果仍然超過大小，調整壓縮質量
            if new_size_mb > max_size_mb:
                for quality in [75, 65, 55, 45]:
                    img_byte_arr = BytesIO()
                    compressed_image.save(img_byte_arr, format='JPEG', quality=quality)
                    img_byte_arr.seek(0)
                    
                    if len(img_byte_arr.getvalue()) / (1024 * 1024) <= max_size_mb:
                        break
            
            return compressed_image
        
        # 如果不需要壓縮，返回原圖
        return image

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
            'apikey': self.TOKEN_LIST[self.TOKEN_INDEX],
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

        for i, img in enumerate(img_list):
            # 檢查並壓縮圖片
            img = self._check_and_compress_image(img,p_idx=i)
            
            # 嘗試使用所有可用的token
            for j in range(self.TOKEN_NUM):
                try:
                    # 每次嘗試都使用當前的token index調用OCR
                    OCR_result_str = self.generate_img_OCR(img, language=language)
                    OCR_result_json = json.loads(OCR_result_str)
                    
                    # 檢查OCR結果
                    if 'ParsedResults' not in OCR_result_json or not OCR_result_json['ParsedResults']:
                        raise Exception(f"No parsed results.")
                    
                    if 'TextOverlay' not in OCR_result_json['ParsedResults'][0]:
                        print(f"The page {i+1} is empty, using default text.")
                        page_lines = [{"LineText": "The page is empty."}] # 使用相同的字典格式
                    else:
                        page_lines = OCR_result_json['ParsedResults'][0]['TextOverlay']['Lines']
                    
                    OCR_results.append(page_lines)
                    break
                    
                except Exception as e:
                    print(f"OCR page {i+1} encounter error with token {self.TOKEN_INDEX+1}: {str(e)}")
                    print(OCR_result_json)
                    
                    if j != self.TOKEN_NUM - 1:
                        print(f"==> Trying next token: {self.TOKEN_LIST[self.TOKEN_INDEX][:6]}")
                        self._change_token()
                    else:
                        print("==> All tokens have been tried and failed.")
                        raise e
            

        pages_list = self._merge_words_to_pages(OCR_results)
        return pages_list


    def _change_token(self):
        self.TOKEN_INDEX = (self.TOKEN_INDEX + 1) % self.TOKEN_NUM
        print(f"==> Changing token to: {self.TOKEN_LIST[self.TOKEN_INDEX][:6]}")
