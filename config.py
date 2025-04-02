import os
from dotenv import load_dotenv

# 確保獲取專案根目錄
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# .env 檔案路徑
ENV_PATH = os.path.join(PROJECT_ROOT, ".env")

# 檢查 .env 是否存在，若無則建立並寫入 PROJECT_ROOT
if not os.path.exists(ENV_PATH):
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.write(f"PROJECT_ROOT={PROJECT_ROOT}\n")

# 讀取 .env 變數
load_dotenv(ENV_PATH)

# 從 .env 讀取 PROJECT_ROOT（確保未來變更時仍然正確）
PROJECT_ROOT = os.getenv("PROJECT_ROOT", PROJECT_ROOT)
