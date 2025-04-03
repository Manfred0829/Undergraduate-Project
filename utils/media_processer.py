import os
from pdf2image import convert_from_path
from PIL import Image
import base64
from io import BytesIO

def read_pdf_to_images(pdf_path):
    """將 PDF 轉換為一系列圖片"""
    images = convert_from_path(pdf_path)
    return images

def _save_image_to_memory(image):
    """將圖片儲存到內存 (BytesIO)"""
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

def convert_image_to_base64(image):
    """將圖片轉換為 Base64 編碼"""
    img_byte_arr = _save_image_to_memory(image)
    return base64.b64encode(img_byte_arr.read()).decode('utf-8')

def convert_base64_to_image(base64_str):
    """將 base64 字串轉換為 PIL Image 物件"""
    try:
        img_data = base64.b64decode(base64_str)
        img = Image.open(BytesIO(img_data))
        return img
    except Exception as e:
        print(f"Base64 轉圖片失敗: {e}")
        return None

def read_image(image_path):
    """讀取圖片並返回 PIL Image 物件"""
    try:
        img = Image.open(image_path)
        return img
    except Exception as e:
        print(f"讀取圖片失敗: {e}")
        return None
    
def save_image(image, save_path):
    """將 PIL Image 儲存到指定路徑"""
    try:
        image.save(save_path)
        print(f"圖片已儲存至: {save_path}")
    except Exception as e:
        print(f"儲存圖片失敗: {e}")

        
def process_pdf_to_base64(pdf_path):
    """將 PDF 轉換為 Base64 格式的圖片"""
    images = read_pdf_to_images(pdf_path)
    base64_images = []
    for img in images:
        base64_image = convert_image_to_base64(img)
        base64_images.append(base64_image)
    return base64_images


'''
# 以下為測試範例
if __name__ == "__main__":
    pdf_path = r"D:\04-大學學業\99_學士班專題\demo\self\3fc8200d20240711111517.pdf"
    base64_images = process_pdf_to_base64(pdf_path)
    for img_base64 in base64_images:
        print(f"Base64 Image: {img_base64[:10]}...")  # 顯示前10個字符
'''