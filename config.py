import os
from dotenv import load_dotenv

# 內部變數（避免直接存取）
_PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
_ENV_PATH = os.path.join(_PROJECT_ROOT, ".env")

# 檢查 .env 是否存在，若無則建立並寫入 _PROJECT_ROOT
if not os.path.exists(_ENV_PATH):
    with open(_ENV_PATH, "w", encoding="utf-8") as f:
        f.write(f"PROJECT_ROOT={_PROJECT_ROOT}\n")

# 讀取 .env 變數
load_dotenv(_ENV_PATH)

# 確保未來變更時仍然正確
_PROJECT_ROOT = os.getenv("PROJECT_ROOT", _PROJECT_ROOT)

def get_project_root():
    """回傳專案根目錄"""
    return _PROJECT_ROOT

def get_env_variable(key, default=None):
    """
    取得環境變數的值，若無則回傳預設值。
    
    :param key: 環境變數名稱
    :param default: 若找不到變數則回傳此值
    :return: 變數值或預設值
    """
    return os.getenv(key, default)
