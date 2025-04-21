import json
import os
import config
import threading

# 全域鎖：模組加載時就建立一次，所有線程共用
IO_lock = threading.Lock()

def write_json(data, relative_path):
    """
    將 JSON 物件寫入專案內的檔案，確保在任何執行環境都能正常運作。

    :param data: 要寫入的 JSON 格式物件
    :param relative_path: 以專案根目錄為基準的相對路徑（例如 "data/sample.json"）
    """
    file_path = os.path.join(config.get_project_root(), relative_path)
    with IO_lock:
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
    with IO_lock:
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_content, f, ensure_ascii=False, indent=4)

        # 讀取 JSON 檔案內容
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)


def extract_keypoints_hierarchy(nested_json: str, flated_json: str):
    """
    從巢狀講義 JSON 檔中提取所有 keypoint，並標註其所屬的章節 / 主題 / 頁面索引。
    將結果儲存成新的 JSON 檔案。
    """

    keypoints_list = []

    for c_idx, chapter in enumerate(nested_json):
        sections = chapter.get('Sections', [])
        for t_idx, topic in enumerate(sections):
            pages = topic.get('Pages', [])
            for p_idx, page in enumerate(pages):
                keypoints = page.get('Keypoints', [])
                for k_idx, k in keypoints:
                    keypoints_list.append({
                        "Title": k.get("Title", ""),
                        "Content": k.get("Content", ""),
                        "Hierarchy": [t_idx, p_idx,k_idx]
                    })

    # 儲存為新的 JSON 檔案
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(keypoints_list, f, ensure_ascii=False, indent=2)

    print(f"✅ Keypoints with hierarchy exported to {output_path}")

