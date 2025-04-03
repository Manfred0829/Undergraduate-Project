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

    def generate_content(self, user_msg, max_retries=3, return_json=False):

        for attempt in range(max_retries):
            try:
                # 呼叫 OpenAI API 進行聊天
                chat_completion = self.model.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": user_msg
                        }
                    ],
                )

                text = chat_completion.choices[0].message.content

                # 若啟用 JSON 模式，嘗試解析 JSON
                if return_json:
                    try:
                        return self._response_to_json(text)
                    except ValueError as e:
                        print(f"⚠️ JSON 解析錯誤: {e} (第 {attempt + 1} 次重試)...")
                        time.sleep(2)  # 等待2秒後重試
                        continue  # 解析失敗則重試 

                # 回傳聊天結果
                return text

            except Exception as e:
                # 捕捉其他錯誤
                print(f"An error occurred: {e} (第 {attempt + 1} 次重試)...")
                time.sleep(2)  # 等待2秒後重試

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
        
    def generate_embedding(self, text_list):

        text_list = [text.replace("\n", " ") for text in text_list]

        response = self.model.embeddings.create(
            input=text_list,
            model="text-embedding-3-small"
        )

        return [response.data[i].embedding for i in range(len(response.data))]



    def generate_img_OCR(self, base64_image, request_msg='What words are in the picture? Only give me the words.'):

        response = self.model.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
            {
                "role": "user",
                "content": [
                {
                    "type": "text",
                    "text": request_msg,
                },
                {
                    "type": "image_url",
                    "image_url": {
                    "url":  f"data:image/jpeg;base64,{base64_image}"
                    },
                },
                ],
            }
            ],
        )
        return response.choices[0].message.content


    def processing_data_example(self):
        """處理數據，要求回應為 JSON"""
        return self.generate_content("str1" + "str2", return_json=True)