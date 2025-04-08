import json
import os
from app import config 

def write_json(data, relative_path):
    """
    將 JSON 物件寫入專案內的檔案，確保在任何執行環境都能正常運作。

    :param data: 要寫入的 JSON 格式物件
    :param relative_path: 以專案根目錄為基準的相對路徑（例如 "data/sample.json"）
    """
    file_path = os.path.join(config.get_project_root(), relative_path)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def read_json(relative_path, default_content=None):
    """
    從專案內的檔案讀取 JSON 物件。如果檔案不存在，則自動建立一個空的 JSON 檔案。

    :param relative_path: 以專案根目錄為基準的相對路徑
    :return: JSON 格式的物件
    """
    file_path = os.path.join(config.get_project_root(), relative_path)
    print(f"File path: {file_path}")

    # 若檔案不存在，創建空 JSON 檔案
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(default_content, f, ensure_ascii=False, indent=4)

    # 讀取 JSON 檔案內容
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

