"""
utils.py
這個模組包含常用的工具函數，可用於各種專案。
"""

import os
import re
import json
import logging
from typing import List, Dict, Any

# 設定 logging（可選）
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 文字處理函數
def clean_text(text: str) -> str:
    """移除多餘空格並轉換為小寫"""
    return " ".join(text.lower().split())

def word_count(text: str) -> int:
    """計算文字中的單詞數"""
    return len(text.split())

# 檔案處理函數
def read_json(file_path: str) -> Dict[str, Any]:
    """讀取 JSON 檔案"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"讀取 JSON 檔案失敗: {e}")
        return {}

def write_json(file_path: str, data: Dict[str, Any]) -> None:
    """寫入 JSON 檔案"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"寫入 JSON 檔案失敗: {e}")

# 字串處理函數
def extract_numbers(text: str) -> List[int]:
    """從字串中提取所有數字"""
    return list(map(int, re.findall(r'\d+', text)))

# 使用方式
if __name__ == "__main__":
    sample_text = "  Hello, this is a test 123 message!  "
    print(clean_text(sample_text))       # ➝ "hello, this is a test 123 message!"
    print(word_count(sample_text))       # ➝ 7
    print(extract_numbers(sample_text))  # ➝ [123]
