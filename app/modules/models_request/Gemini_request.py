import concurrent.futures
import time
import json

from app.modules.module_template import LazySingleton

class GeminiRequest(LazySingleton):
    model = None
    genai = None

    def initialize(self):
        """初始化方法"""
        import config 
        import google.generativeai as genai

        # 獲取 Api key
        GOOGLE_API_KEY = config.get_env_variable("GOOGLE_API_KEY")
        genai.configure(api_key=GOOGLE_API_KEY)

        # 確保 model 存在於 self 內
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.genai = genai

        # 設定已初始化
        self._initialized = True

    def generate_content(self, prompt, max_retries=3, timeout=10, return_json=False):
        """呼叫 Gemini API，可選擇是否轉換為 JSON"""
        for attempt in range(max_retries):
            try:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self.model.generate_content, prompt)
                    response = future.result(timeout=timeout)  # 設定超時

                if response and hasattr(response, "text"):
                    text = response.text

                    # 若啟用 JSON 模式，嘗試解析 JSON
                    if return_json:
                        try:
                            return self._response_to_json(text)
                        except ValueError as e:
                            print(f"⚠️ JSON 解析錯誤: {e} (第 {attempt + 1} 次重試)...")
                            continue  # 解析失敗則重試

                    return text  # 純文本模式，直接返回

                raise ValueError("API 回應無效")  # 若 response 為 None，則拋出錯誤

            except concurrent.futures.TimeoutError:
                print(f"⚠️ 請求超時 (第 {attempt + 1} 次重試)...")
            except Exception as e:
                print(f"⚠️ 發生錯誤: {e} (第 {attempt + 1} 次重試)...")

            time.sleep(2)  # 等待 2 秒後重試

        raise RuntimeError("⛔ 超過最大重試次數，請求失敗")

    def _response_to_json(self, response_str: str):
        """將 Gemini 回應轉換為 JSON"""
        try:
            response_str = response_str.replace("```json", "").replace("```", "")
            return json.loads(response_str)
        except json.JSONDecodeError as e:
            raise e

    def generate_embedding(self,textList, task_type="SEMANTIC_SIMILARITY"):
        result = self.genai.embed_content(
            model="models/embedding-001",
            content=textList,
            task_type=task_type) # clustering #SEMANTIC_SIMILARITY #RETRIEVAL_DOCUMENT #RETRIEVAL_QUERY
        return result['embedding']


    def processing_data_example(self):
        """處理數據，要求回應為 JSON"""
        return self.generate_content("str1" + "str2", return_json=True)