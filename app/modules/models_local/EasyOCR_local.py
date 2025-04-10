

import json
import numpy as np
import time
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt

from app.modules.module_template import LazySingleton

class EasyOCRLocal(LazySingleton):
    model = None

    def __new__(cls, languages=None):
        instance = super().__new__(cls)
        instance._languages = languages if languages is not None else ['en', 'ch_tra']
        return instance

    def initialize(self):
        import easyocr
        self._initialized = True

        self.languages = self._languages
        self.model = easyocr.Reader(self.languages)
        print(f"✅ 初始化EasyOCR，Accepted Languages： {self.languages}")


    def generate_img_OCR(self, pil_image):
        """直接接受 PIL 圖片物件，並使用 EasyOCR 執行辨識"""

        if not isinstance(pil_image, Image.Image):
            raise ValueError("❌ 輸入必須是 PIL.Image.Image 物件")

        # 轉成 numpy array（EasyOCR 支援）
        image_np = np.array(pil_image)

        # 執行辨識
        results = self.model.readtext(image_np)

        return results
    
    def _isSameLine(self,sum_top, sum_bottom, count, box):

        avg_height = (sum_top - sum_bottom) / count
        avg_mid = (sum_top + sum_bottom) / (count*2)
        threshold = avg_height * 0.6

        if (abs( avg_mid - (box[3][1]+box[0][1])/2 ) > threshold):
            return False
        elif (abs(avg_height - (box[3][1]-box[0][1])) > threshold):
            return False
        else:
            return True

    # 獲得每行各自的boxes物件
    def _get_lines_boxes(self,boxes):

        merged_lines = []
        boxes = sorted(boxes, key=lambda x: x[0][1])  # 按 y 坐標排序
        current_line = [boxes[0]]
        sum_top = boxes[0][3][1]
        sum_bottom = boxes[0][0][1]
        sum_weidht = 0

        for box in boxes[1:]:
            # 如果新框的 y 坐標與當前行的差異小於 threshold，則將其合併
            if self._isSameLine(sum_top, sum_bottom, len(current_line), box):
                current_line.append(box)
                sum_top += box[3][1]
                sum_bottom += box[0][1]
            else:
                # 如果新的框位於新的一行，將當前行加入結果，並重置 current_line
                merged_lines.append(current_line)
                current_line = [box]
                sum_top = box[3][1]
                sum_bottom = box[0][1]

        # did not set current_line to None
        if current_line:
            merged_lines.append(current_line)

        # 根據dx寬度決定橫向是否要切分
        splited = []
        for line in merged_lines:
            line = sorted(line, key=lambda x: x[0][0])  # 按 x 坐標排序
            sum_gap = line[0][3][1] - line[0][0][1]
            count = 1
            start = 0

            for i in range(len(line)-1):
                dx = line[i+1][0][0] - line[i][3][0]
                if dx > (sum_gap*7 / count):
                    splited.append(line[start:i+1])
                    start = i+1
                    sum_gap = line[i+1][3][1] - line[i+1][0][1]
                    count = 1
                else:
                    sum_gap += dx
                    count += 1

            if (line[start:] != []):
                splited.append(line[start:])

        #print(splited)
        splited = sorted(splited, key=lambda line: line[0][0][1])

        return splited
    

    def _get_lines_box(self,lines_boxes):
        """
        將多行文字的框合併為行級別的大框

        Args:
            lines_boxes: List[List[box]]
                每行是一組 box，每個 box 是一組四點座標（四個 [x, y]）

        Returns:
            List[Tuple[int, int, int, int]]
                每行合併後的大框座標：(x1, y1, x2, y2)
        """
        lines_box = []

        for line in lines_boxes:
            # 計算整行框的邊界：取最小的左上角和最大的右下角
            x1 = int(min([min(box[0][0], box[3][0]) for box in line]))
            y1 = int(min([min(box[0][1], box[1][1]) for box in line]))
            x2 = int(max([max(box[1][0], box[2][0]) for box in line]) + 1)
            y2 = int(max([max(box[2][1], box[3][1]) for box in line]) + 1)

            lines_box.append((x1, y1, x2, y2))

        return lines_box

    def _draw_lines_boxes(self, pil_image, lines_boxes, save_path=None):
        """
        在原始圖片上畫出行框。

        Args:
            pil_image: PIL.Image
                要處理的原始圖片。
            lines_boxes: List[Tuple[int, int, int, int]]
                包含每行框位置的座標 (x1, y1, x2, y2)。
            save_path: str, optional
                如果提供，處理後的圖片將保存到此路徑。如果為 None，不保存圖片。
        
        Returns:
            PIL.Image: 處理後的圖片。
            str: 保存的圖片路徑（如果有保存）。
        """
        # 複製一個新圖片，以免修改原始圖片
        pil_image = pil_image.copy()
        
        # 使用 PIL 的 ImageDraw 進行繪製
        draw = ImageDraw.Draw(pil_image)

        for box in lines_boxes:
            x1, y1, x2, y2 = box
            draw.rectangle([x1, y1, x2, y2], outline="red", width=3)  # 繪製紅色矩形框

        # 保存處理後的圖片
        saved_path = None
        if save_path is not None:  # 如果提供了保存路徑或默認保存
            import os
                
            pil_image.save(save_path)
            saved_path = save_path
            print(f"✅ 已保存處理後的圖片至: {saved_path}")
        
        return pil_image, saved_path

    def _crop_lines_from_PIL(self, pil_image, lines_box):
        """
        根據提供的行框 (lines_box) 將原始圖片切割成多個小圖片。

        Args:
            pil_image: PIL.Image
                要切割的原始圖片。
            lines_box: List[Tuple[int, int, int, int]]
                包含每行框位置的座標 (x1, y1, x2, y2)。

        Returns:
            List[PIL.Image]
                切割後的小圖片列表。
        """
        cropped_images = []
        
        for box in lines_box:
            x1, y1, x2, y2 = box
            # 根據行框 (x1, y1, x2, y2) 將圖片切割
            cropped_image = pil_image.crop((x1, y1, x2, y2))
            cropped_images.append(cropped_image)

        return cropped_images


    def processing_lines_bounding_box(self, pil_image, draw_result=False, save_path=None):
        #print("Step 1")
        OCR_result = self.generate_img_OCR(pil_image)
        #print("Step 2")
        lines_boxes = self._get_lines_boxes([res[0] for res in OCR_result])
        #print("Step 3")
        lines_box = self._get_lines_box(lines_boxes)

        # 繪製行框並保存
        if draw_result:
            #print("Step 3.5")
            self._draw_lines_boxes(pil_image, lines_box, save_path)
            # 如需保存處理後的圖像，可以在這裡添加保存代碼

        #print("Step 4")
        cropped_images = self._crop_lines_from_PIL(pil_image, lines_box)

        return cropped_images
