import os

# 取得當前檔案所在目錄的上層，也就是專案根目錄
PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

def get_project_root():
    """回傳專案根目錄路徑"""
    return PROJECT_ROOT
