import concurrent.futures
import time
from modules.module_template import LazySingleton
import json
import re

class OpenAIRequest(LazySingleton):
    model = None

    def initialize(self):
        """初始化方法"""
        import config
        from openai import OpenAI

        client = OpenAI(
            api_key = config.get_env_variable("OPENAI_API_KEY")
        )

        # 確保 model 存在於 self 內
        self.model = client

        # 設定已初始化
        self._initialized = True

    def generate_content(self, prompt, max_retries=3, timeout=10, return_json=False):
        """呼叫 OpenAI API，可選擇是否轉換為 JSON"""
        for attempt in range(max_retries):
            try:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self._openai_chat, prompt)
                    response = future.result(timeout=timeout)  # 設定超時

                if response and hasattr(response, "choices"):
                    text = response.choices[0].message.content

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
            # 先去除 ```json
            temp = re.sub(r'^.*?```json', '', response_str, flags=re.DOTALL)

            # 使用正則表達式將 ``` 及其後的內容去除
            temp = re.sub(r'```.*', '', temp, flags=re.DOTALL)
            return json.loads(temp)
        
        except json.JSONDecodeError as e:
            print(response_str)
            raise e
        

    def _openai_chat(self,user_msg):

        chat_completion = self.model.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": user_msg
                }
            ],
        )
        return chat_completion



    def processing_data_example(self):
        """處理數據，要求回應為 JSON"""
        return self.generate_content("str1" + "str2", return_json=True)