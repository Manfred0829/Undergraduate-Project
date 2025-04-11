import concurrent.futures
import time
import json
import re

from app.modules.module_template import LazySingleton

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

        # text_list = [text.replace("\n", " ") for text in text_list]

        response = self.model.embeddings.create(
            input=text_list,
            model="text-embedding-3-small"
        )

        return [response.data[i].embedding for i in range(len(response.data))]



    def generate_img_OCR(self, base64_image, request_msg='What words are in the picture? Only give me the words.', max_retries=3):
        for attempt in range(max_retries):
            try:
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
            
            except Exception as e:
                if "rate_limit_exceeded" in str(e):
                    wait_time = 2 if attempt < max_retries - 1 else 5
                    print(f"速率限制錯誤，等待 {wait_time} 秒後重試 (第 {attempt + 1} 次)...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"發生錯誤: {e} (第 {attempt + 1} 次重試)...")
                    time.sleep(2)

        raise RuntimeError("⛔ 超過最大重試次數，請求失敗")


    def processing_data_example(self):
        """處理數據，要求回應為 JSON"""
        return self.generate_content("str1" + "str2", return_json=True)
    

    def processing_notes_repair(self,text):
        prompt_prefix = """The content below is the OCR result which may have some missing words. Please do your best to repair the original meaning of the text. Do not delete any parts that cannot be repaired, use the original language same as given texts.
        
        OCR result:
        """

        return self.generate_content(prompt_prefix+text)
    
    def processing_notes_extract_keypoints(self,text):
        prompt_prefix = """The content below is the text extracted from a student notes.

        Task:
        1. Seperate the text into one or many key points accroding to different concept.
        2. Arrange the key point in the form of bullet points if possible.
        3. Give every key points a short describe around 5 words as the title.
        4. Output the result in json format: [{"Title":"the description of key point", "Content":"the content of key point"}, {...}]
        5. If the text content does not include any key points, output the empty json file: [].
        6. All of the output texts using the language same as given student notes texts (including Title result and Content result).

        text of a student notes:
        """

        return self.generate_content(prompt_prefix+text,return_json=True)


    def processing_handouts_extract_keypoints(self,text):
        prompt_prefix = """The content below is the text extracted from a page of lecture ppt.

        Task:
        1. Seperate the text into one or many key points accroding to different concept.
        2. Arrange the key point in the form of bullet points if possible.
        3. Give every key points a short describe around 5 words as the title.
        4. Output the result in json format: [{"Title":"the description of key point", "Content":"the content of key point"}, {...}]
        5. If the text content does not include any key points (e.g. The page is title page or outline page etc.), output the empty json file: [].
        6. All of the output texts using the language same as given ppt page texts (including Title result and Content result).

        Below is the text of a ppt page:
        """

        return self.generate_content(prompt_prefix+text,return_json=True)
    
    def processing_handouts_page_info(self,text):
        prompt_prefix = """The content below is the text extracted from a page of lecture ppt.

        Task:
        1. If the page content include concept description, give this page a concept name less than 10 words and output as the json format: {"Type":"Concept", "Content":"the concpet of this page"}
        2. If the page is a title page, output as the json format: {"Type":"Title", "Content":"the title name"}
        3. If the page is a outline page, output as the json format: {"Type":"Outline", "Content":"the outline items"}

        Below is the text of a ppt page:
        """

        return self.generate_content(prompt_prefix+text,max_retries=3,return_json=True)
    

    def processing_handouts_extract_topic(self,pages_info_json):

        prompt = f"""
        You are given structured content describing each page in a lecture PowerPoint. Each item includes the page number, page type (Title, Outline, Concept), and a brief page description.

        ### Task
        1. Group the pages into **multiple coherent topics** based on the sequence and content of the pages.
        2. Each topic must be represented by a short descriptive title.
        3. For each topic, identify the **starting page number** where that topic begins.
        4. The number of topics should be **less than or equal to {len(pages_info_json)//2}**.

        ### Output Format (JSON array)
        [
        {{
            "Topic": "Short summary of the topic",
            "Starting_page": int
        }},
        ...
        ]

        ### Lecture Pages Input:
        
        """
        
        for i, page in enumerate(pages_info_json):
            temp = f"Page {i+1}, Type: {page['Type']}, Description: {page['Content'].replace('\n','    ')}\n"
            prompt += temp
            #print(temp)

        return self.generate_content(prompt,max_retries=2,return_json=True)
    


    def processing_handouts_extract_section(self, topic_titles: list):
        """
        將多個主題（topic）根據標題進行語意分群，劃分為更上層的 section。
        
        Args:
            topic_titles (List[str]): 每個 topic 的簡要標題（由前一層產出）

        Returns:
            List[Dict]: 包含每個 section 的標題與其起始 topic 編號（從 1 開始）
        """

        prompt = f"""
        You are given a list of topic titles extracted from a lecture. Your task is to group them into **sections** that represent higher-level categories of the lecture structure.

        ### Task
        1. Group the topics into **coherent sections**.
        2. Each section should contain **several related topics**.
        3. For each section, give a **short descriptive title**.
        4. For each section, indicate the **starting topic number** (starting from 1).
        5. The number of sections should be **less than or equal to {max(1, len(topic_titles) // 2)}**.

        ### Output Format (JSON array)
        [
        {{
            "Section": "Short summary of the section",
            "Starting_topic": int
        }},
        ...
        ]

        ### Lecture Topics:
        """

        for i, title in enumerate(topic_titles):
            prompt += f"Topic {i + 1}: {title}\n"

        return self.generate_content(prompt, max_retries=2, return_json=True)
    

    def processing_handouts_extract_chapter(self, filename_without_ext, first_page):

        prompt = f"""
        You are given the filename and the content of the first page of a lecture handout (usually the title slide). Based on these, extract the **name of the main chapter or unit** this lecture belongs to.

        ### Task
        1. Understand the high-level theme or subject of the lecture based on the filename and first-page content.
        2. The chapter name should be **concise but descriptive**, such as "Chapter 3: Process Management" or "Unit 5: Introduction to AI".
        3. Do not include unrelated or overly verbose information.
        4. Output only one field as JSON format:

        ### Output Format
        {{
            "Chapter": "..."
        }}

        ### Input Information

        **Filename**: {filename_without_ext}

        **First Page Content**:
        {first_page.strip()}
        """

        return self.generate_content(prompt, max_retries=2, return_json=True)


    def processing_handouts_weights(self, subject, keypoints_flatten):
        prompt = f"""
        You are given one of the keypoints in the subject {subject}, please complete below tesk:

        1.Evaluate the difficulty of the keypoint (classified as simple, normal, or difficult), represented by a score from 1 to 3.
        2.Evaluate the importance of the keypoint (classified as irrelevant, general, key point, or very important), represented by a score from 0 to 3.
        3.Output the result in the following JSON format:
        {{
        "Difficulty": 1,
        "Importance": 1
        }}
        Below is a keypoint about the subject {subject}:
        """

        weights = []
        for keypoint in keypoints_flatten:
            weight = self.generate_content(prompt + keypoint, return_json=True)
            weights.append(weight)

        return weights