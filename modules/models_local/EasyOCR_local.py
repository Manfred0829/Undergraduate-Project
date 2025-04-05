'''
import sys
import os

# 找到專案根目錄，並加入 sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
# test
# ==============================================================================
'''

import json
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

from modules.module_template import LazySingleton

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

    def _draw_lines_boxes(self, pil_image, lines_boxes):
        """根據行方框在圖片上繪製框並顯示"""
        # 轉換 PIL 物件到可繪製的物件
        draw = ImageDraw.Draw(pil_image)

        # 繪製每一個行框
        for box in lines_boxes:
            x1, y1, x2, y2 = box
            draw.rectangle([x1, y1, x2, y2], outline="red", width=3)  # 繪製紅色矩形框

        # 顯示圖片（而非儲存）
        plt.imshow(pil_image)
        plt.axis('off')  # 不顯示軸線
        plt.show(block=False)  # 顯示圖片

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


    def processing_lines_bounding_box(self, pil_image,draw_result=False):
        #print("Step 1")
        OCR_result = self.generate_img_OCR(pil_image)
        #print("Step 2")
        lines_boxes = self._get_lines_boxes([res[0] for res in OCR_result])
        #print("Step 3")
        lines_box = self._get_lines_box(lines_boxes)

        # 繪製行框並顯示
        if draw_result:
            #print("Step 3.5")
            self._draw_lines_boxes(pil_image, lines_box)

        #print("Step 4")
        cropped_images = self._crop_lines_from_PIL(pil_image,lines_box)
        
        return cropped_images






# =====================

'''
def main():
    # 創建 YourClass 類的實例
    your_class_instance = EasyOCRLocal()

    # 打開一個圖片檔案（你可以替換成你自己的圖片檔案）
    pil_image = Image.open(r"self\handwritten_goodnotes_word.jpg")  # 替換為你的圖片路徑

    # 執行處理並顯示結果
    your_class_instance.processing_lines_bounding_box(pil_image)


if __name__ == "__main__":
    main()
'''