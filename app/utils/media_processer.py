import os
from pdf2image import convert_from_path
from PIL import Image
import base64
from io import BytesIO
from PyPDF2 import PdfReader

from graphviz import Digraph

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

def convert_PIL_to_base64(image):
    """將圖片轉換為 Base64 編碼"""
    img_byte_arr = _save_image_to_memory(image)
    return base64.b64encode(img_byte_arr.read()).decode('utf-8')

def convert_base64_to_PIL(base64_str):
    """將 base64 字串轉換為 PIL Image 物件"""
    try:
        img_data = base64.b64decode(base64_str)
        img = Image.open(BytesIO(img_data))
        return img
    except Exception as e:
        print(f"Base64 轉圖片失敗: {e}")
        return None

def read_image_to_PIL(image_path):
    """讀取圖片並返回 PIL Image 物件"""
    try:
        img = Image.open(image_path)
        return img
    except Exception as e:
        print(f"讀取圖片失敗: {e}")
        return None
    
def save_image_from_PIL(image, save_path):
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
        base64_image = convert_PIL_to_base64(img)
        base64_images.append(base64_image)
    return base64_images


def get_num_pages(pdf_path):
    """高效獲取 PDF 頁數（不轉圖片）"""
    reader = PdfReader(pdf_path)
    return len(reader.pages)


def generate_chapter_hierarchy_graph(chapter: dict, save_path='chapter_tree', exclude_keys=None, max_str_len=30):
    """
    將巢狀講義章節結構可視化為樹狀圖，並儲存為圖片。
    
    :param chapter: 巢狀 JSON 格式的講義資訊（含 Sections / Topics / Pages / Keypoints）
    :param save_path: 輸出圖檔名稱（不含副檔名）
    :param exclude_keys: 要忽略的 key 名稱，例如 ['Embedding', 'Content']
    :param max_str_len: 欄位值過長時的最大顯示字數
    """

    dot = Digraph(comment='Lecture Chapter Hierarchy', format='png')

    dot.attr(rankdir='LR')  # TB=垂直, LR=水平
    dot.attr(dpi='300', ranksep='1.0', nodesep='0.5')  # 設定整體的間距

    # 調整圖表屬性：上方顯示 label，並靠左對齊
    dot.attr(labeljust="l", labelloc="t")

    # 使用 HTML-like label 當作圖例
    dot.attr(label=r'''<
    <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
    <TR><TD BGCOLOR="#bbdefb">Chapter</TD></TR>
    <TR><TD BGCOLOR="#c8e6c9">Section</TD></TR>
    <TR><TD BGCOLOR="#fff9c4">Topic</TD></TR>
    <TR><TD BGCOLOR="#f8bbd0">Keypoint</TD></TR>
    </TABLE>
    >''')

    cid = "0"
    dot.node(f"{cid}",chapter['Chapter'],shape='box', style='filled',fillcolor='#bbdefb')
    
    for s_idx, section in enumerate(chapter['Sections']):
        sid = f'section_{s_idx}'
        dot.node(sid, f"{section['Section']}",shape='box', style='filled',fillcolor='#c8e6c9')
        dot.edge(cid, sid)  # Section → Topic

        for t_idx, topic in enumerate(section['Topics']):
            tid = f'topic_{s_idx}_{t_idx}'
            dot.node(tid, f"{topic['Topic']}",shape='box', style='filled',fillcolor='#fff9c4')
            dot.edge(sid, tid)  # Section → Topic

            topic_content = ""

            for p_idx, page in enumerate(topic['Pages']):
                for k_idx, kp in enumerate(page.get('Keypoints', [])):
                    title = kp.get("Title", "")
                    if title:  # 確保有標題
                        if topic_content:  # 如果有已有內容，則以換行符號分隔
                            topic_content += ",\n" + title
                        else:  # 第一個標題不需要加逗號
                            topic_content = title

            # 如果有 keypoints 內容，將其添加為新 node，並附加到 topic
            if topic_content:
                dot.node(f"{tid}_keypoints", topic_content, shape='box', style='filled',fillcolor='#f8bbd0')
                dot.edge(tid, f"{tid}_keypoints")  # Topic → Keypoints


    dot.render(save_path, cleanup=True)
    print(f"✅ 樹狀圖已儲存為 {save_path}.png")

