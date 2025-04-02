import os
from dotenv import load_dotenv

def get_project_root():
    """回傳專案根目錄路徑，若 .env 檔案不存在則創建並儲存根目錄。"""
    
    # 檢查是否存在 .env 檔案
    if not os.path.exists('.env'):
        # 如果 .env 不存在，將專案根目錄寫入 .env
        project_root = os.path.abspath(os.path.dirname(__file__))
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(f"PROJECT_ROOT={project_root}\n")
        return project_root
    
    # 如果 .env 存在，從中讀取 PROJECT_ROOT
    load_dotenv()  # 讀取 .env 檔案
    project_root = os.getenv('PROJECT_ROOT')
    
    # 如果 .env 檔案中沒有 PROJECT_ROOT 變數，則創建並返回
    if project_root is None:
        project_root = os.path.abspath(os.path.dirname(__file__))
        with open('.env', 'a', encoding='utf-8') as f:
            f.write(f"PROJECT_ROOT={project_root}\n")
    
    return project_root

