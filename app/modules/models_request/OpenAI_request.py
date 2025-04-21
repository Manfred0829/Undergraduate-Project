import concurrent.futures
import time
import json
import re
import config

from app.modules.module_template import LazySingleton

class OpenAIRequest(LazySingleton):
    model = None

    def initialize(self):
        """初始化方法"""
        from openai import OpenAI

        client = OpenAI(
            api_key = config.get_env_variable("OPENAI_API_KEY")
        )

        # 確保 model 存在於 self 內
        self.model = client

        # 設定已初始化
        self._initialized = True

    def generate_content(self, user_msg, max_retries=3, return_json=False):
        # 避免API頻率過高
        time.sleep(0.1)
        
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

        # 過濾空字符串和無效值，並確保每個項目都是字符串
        filtered_text_list = []
        for text in text_list:
            if text and isinstance(text, str) and len(text.strip()) > 5:  # 確保文字不為空且至少有5個字符
                filtered_text_list.append(text.replace("\n", " "))
            else:
                # 對於無效文本，使用佔位符，以保持索引一致性
                filtered_text_list.append("Empty content placeholder")
        
        try:
            response = self.model.embeddings.create(
                input=filtered_text_list,
                model="text-embedding-3-small"
            )
            
            return [response.data[i].embedding for i in range(len(response.data))]
        
        except Exception as e:
            print(f"嵌入生成錯誤: {e}")
            # 如果發生錯誤，返回空矩陣（維度1536，即text-embedding-3-small的向量維度）
            return [[0.0] * 1536 for _ in range(len(filtered_text_list))]



    def generate_img_OCR(self, base64_image, request_msg='What words are in the picture? Only give me the words.', max_retries=3):
        # 避免API頻率過高
        time.sleep(0.1)

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
        '''
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
        '''

        prompt_prefix = """The content below is the text extracted from a page of lecture ppt.

        Task:
        1. Identify one or more **key points** from the text. A key point should represent a **complete concept or topic**, not just a single sentence.
        2. If multiple sentences describe the **same topic**, group them into one key point.
        3. Avoid over-segmenting. Do **not** treat every sentence as a separate key point unless they are clearly unrelated.
        4. For each key point, give it:
            - A short title (around 5 words) summarizing the concept.
            - The full content (may include several related sentences).
        5. Present the output in JSON format: [{"Title": "brief title", "Content": "detailed explanation"}, {...}]
        6. If the text includes no key points (e.g., a title or agenda slide), return an empty JSON: []
        7. Output must use the **same language** as the input slide (for both title and content).
        8. Your role is like a student summarizing the slide into meaningful study notes.

        Below is the text of a ppt page:
        """


        return self.generate_content(prompt_prefix+text,return_json=True)
    
    def processing_notes_correct(self,subject,note):
        prompt_prefix = f"""The content below is a student note of the subject {subject}, complete the following task.

        Task:
        1. If the note contains conceptual errors, please correct the Content description and output as the json format: {{"isCorrected":true, "Corrected_Content":"the corrected content of the note"}}
        2. If the note does not contains conceptual errors, please output as the json format: {{"isCorrected":false}}

        text of a student note:
        """
        prompt_note = "Title: " + note['Title'] + "\nCnotent: " + note['Content']
        return self.generate_content(prompt_prefix+prompt_note,return_json=True)


    def processing_handouts_extract_keypoints(self,text):
        '''
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
        '''
        '''
        prompt_prefix = """The content below is the text extracted from a page of lecture ppt.

        Task:
        1. Identify one or more **key points** from the text. A key point should represent a **complete concept or topic**, not just a single sentence.
        2. If multiple sentences describe the **same topic**, group them into one key point.
        3. Avoid over-segmenting. Do **not** treat every sentence as a separate key point unless they are clearly unrelated.
        4. For each key point, give it:
            - A short title (around 5 words) summarizing the concept.
            - The full content (may include several related sentences).
        5. Present the output in JSON format: [{"Title": "brief title", "Content": "detailed explanation"}, {...}]
        6. If the text includes no key points (e.g., a title or agenda slide), return an empty JSON: []
        7. Output must use the **same language** as the input slide (for both title and content).
        8. Your role is like a student summarizing the slide into meaningful study notes.

        Below is the text of a ppt page:
        """
        '''
        
        prompt_prefix = """The content below is the text extracted from a page of lecture ppt.

        Task:
        1. Extract one or more key points. A key point should represent a meaningful concept or topic.
        2. If multiple sentences describe the same topic (e.g., advantages of Message Passing), group them into a single key point.
        3. For each key point:
            - Use a short title (around 3–6 words) summarizing the concept.
            - In the "Content", list main ideas **in a concise bullet-point style**, separated by line breaks or semicolons.
            - Do not write long explanatory paragraphs.
            - Avoid over-segmenting (do NOT treat each bullet as a separate key point).
        4. Present the result in the following JSON format:
            [{"Title": "short topic title", "Content": "• point one\\n• point two\\n• point three"}, {...}]
        5. If the slide has no meaningful content (e.g., a title page, outline page, grading scale page, etc.), return an empty list: []
        6. Use the **same language** as the input text (for both Title and Content).
        7. Write like a student summarizing notes with brief bullet points.

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
            content = page['Content'].replace("\n", " ")
            temp = f"Page {i+1}, Type: {page['Type']}, Description: {content}\n"
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

        # 檢查輸入參數
        if not first_page or not isinstance(first_page, str) or len(first_page.strip()) < 5:
            # 如果沒有有效的第一頁文本，則直接使用檔名作為章節名稱
            return {"Chapter": filename_without_ext or "未命名章節"}

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

        try:
            result = self.generate_content(prompt, max_retries=2, return_json=True)
            # 驗證返回結果
            if isinstance(result, dict) and "Chapter" in result and result["Chapter"]:
                return result
            else:
                # 如果返回格式不符合預期
                return {"Chapter": filename_without_ext or "未命名章節"}
        except Exception as e:
            print(f"提取章節時發生錯誤: {e}")
            # 發生異常時使用檔名
            return {"Chapter": filename_without_ext or "未命名章節"}


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
        default_weight = {"Difficulty": 2, "Importance": 2}  # 預設中等難度和重要性
        
        # 限制處理數量，避免API費用過高或超時
        max_keypoints = min(len(keypoints_flatten), 100)
        
        for i, keypoint in enumerate(keypoints_flatten[:max_keypoints]):
            try:
                # 確保文本不為空
                if not keypoint or not isinstance(keypoint, str) or len(keypoint.strip()) < 10:
                    weights.append(default_weight)
                    continue
                
                # 限制文本長度
                if len(keypoint) > 1000:
                    keypoint = keypoint[:1000] + "..."
                
                weight = self.generate_content(prompt + keypoint, return_json=True)
                
                # 驗證結果格式
                if not isinstance(weight, dict) or "Difficulty" not in weight or "Importance" not in weight:
                    weights.append(default_weight)
                else:
                    # 確保值在有效範圍內
                    difficulty = min(max(weight.get("Difficulty", 2), 1), 3)
                    importance = min(max(weight.get("Importance", 2), 0), 3)
                    weights.append({"Difficulty": difficulty, "Importance": importance})
                
            except Exception as e:
                print(f"處理第 {i+1} 個關鍵點權重時發生錯誤: {e}")
                weights.append(default_weight)
            
            # 降低API呼叫頻率
            time.sleep(0.2)
        
        # 如果實際關鍵點數量超過處理數量，使用預設權重填充
        while len(weights) < len(keypoints_flatten):
            weights.append(default_weight)
            
        return weights
    

    def generate_question(self,subject, keypoint_json):
        prompt = f"""
        You are given one of the keypoints in the subject {subject}, please complete below tesk:

        Create a multiple-choice question with four options, numbered 1 to 4, and output it in the following JSON format:
        {{
            "question": "question text",
            "options": ["option1", "option2", "option3", "option4"],
            "correct_answer": int (from 0 to 3 representing the index of the correct option)
        }}

        Below is a keypoint about the subject {subject}:
        """

        keypoint_prompt = "Title: " + keypoint_json["Title"] + "\nContent: " + keypoint_json["Content"]+ "\n"

        # 暫不實現將筆記加入prompt
        """
        if "Notes" in keypoint_json: # 如果有筆記
            for i, note in keypoint_json['Notes']:
                keypoint_prompt += f"Note {i+1}: " + note[]
        """

        response = self.generate_content(prompt + keypoint_prompt, return_json=True)
        
        # 格式化並轉換返回的數據以匹配前端期望
        if isinstance(response, dict) and "correct_answer" in response:
            # 將數字索引 (0-3) 轉換為字母 (A-D)
            correct_index = response["correct_answer"]
            if isinstance(correct_index, int) and 0 <= correct_index <= 3:
                answer_letter = chr(65 + correct_index)  # A, B, C, D
                
                # 創建新的返回對象
                formatted_response = {
                    "question": response.get("question", ""),
                    "options": response.get("options", []),
                    "answer": answer_letter,  # 前端期望的是 A, B, C, D
                    "explanation": response.get("explanation", ""),  # 包含解釋，如果有的話
                    "Keypoints_Index": keypoint_json.get("Keypoints_Index", 0)  # 包含重點索引
                }
                return formatted_response
            
        # 如果返回的數據格式不正確或沒有正確答案，創建一個預設返回
        return {
            "question": "無法生成有效的問題。請重試或選擇不同的重點。",
            "options": ["選項1", "選項2", "選項3", "選項4"],
            "answer": "A",
            "explanation": "系統生成問題時出錯",
            "Keypoints_Index": keypoint_json.get("Keypoints_Index", 0)
        }
    


    # 偵測是否包含中文的簡單方法
    def _contains_chinese(self, text):
        return re.search(r'[\u4e00-\u9fff]', text) is not None

    # 主函數：對陣列中的字串處理
    def processing_embedding(self, text_list):
        text_list_trans = []
        for text in text_list:
            if self._contains_chinese(text):
                translated = self.generate_content("將以下內容翻譯成英文：\n" + text)
                text_list_trans.append(translated)
            else:
                text_list_trans.append(text)
        
        return self.generate_embedding(text_list_trans)

