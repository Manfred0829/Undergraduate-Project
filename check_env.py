import sys
import os
from pathlib import Path
import site

"""
   /虛擬環境目錄（非專案根目錄）
   ├── bin/
   │   └── python          # Python 解釋器
   └── lib/
       └── python3.12/
           └── site-packages/  # 安裝的套件位置
"""

def check_environment():
    # 獲取當前環境信息
    project_name = "Undergraduate-Project"
    project_root = Path(__file__).parent.resolve()  # 專案根目錄
    current_python = sys.executable # 虛擬環境中的 Python 解釋器路徑
    search_path = sys.path # 搜尋路徑
    virtual_env = os.environ.get('VIRTUAL_ENV') # 虛擬環境目錄  
    
    
    print(f"\n環境檢查結果：")
    print(f"\n專案根目錄: {project_root}")
    print(f"\n虛擬環境路徑: {virtual_env}")
    print(f"\n虛擬環境中的 Python 解釋器路徑: {current_python}")
    print(f"\n所有搜尋路徑：")
    for path in sys.path:
        print(f"- {path}")

    """
    『目前使用』的 Python 解釋器路徑 (Terminal)：
    python -c "import sys; print(sys.path)"
    """

    # 檢查 1: 確認是否在虛擬環境中
    if not virtual_env:
        print("\n警告：目前不在虛擬環境中運行！")
        return False
        
    # 檢查 2: 確認 Python 解釋器是否來自正確的虛擬環境
    if not current_python.startswith(virtual_env):
        print("\n警告：Python 解釋器不在當前虛擬環境中！")
        return False
    
    # 檢查 3: 確認專案檔案位置是否正確
    if str(project_root).startswith(virtual_env):
        print("\n警告：專案檔案不應該放在虛擬環境目錄中！")
        return False
        
    # 檢查 4: 掃描專案中的 Python 檔案
    print("\n檢查專案中的 Python 檔案：")
    python_files = list(project_root.rglob("*.py"))
    
    for py_file in python_files:
        relative_path = py_file.relative_to(project_root)
        print(f"\n檢查檔案: {relative_path}")
        
        # 確認檔案不在虛擬環境目錄中
        if str(py_file).startswith(virtual_env):
            print(f"警告：此檔案位於虛擬環境目錄中！")
            continue
            
        # 檢查是否可以導入（可選）
        module_path = str(py_file.parent)
        if module_path not in sys.path:
            print(f"Warning: 目錄 {module_path} 不在搜尋路徑中")
    
    # 檢查專案根目錄是否在 Python 路徑中
    if project_root not in sys.path:
        print("\n建議：將專案根目錄加入搜尋路徑，可以：")
        print("1. 安裝專案套件：pip install -e .")
        print("2. 設定 PYTHONPATH 環境變數")
        print("3. 在程式中手動加入系統路徑")
    
    # 檢查是否已安裝為開發模式
    try:
        import Undergraduate_Project
        print("\n專案已正確安裝")
    except ImportError:
        print("\n建議：執行 'pip install -e .' 安裝專案")
    
    print("\n環境檢查完成！")
    return True

    # # 檢查 site-packages
    # for site_dir in site.getsitepackages():
    #     egg_link = Path(site_dir) / f"{project_name}.egg-link"
    #     if egg_link.exists():
    #         print(f"\n找到 egg-link：{egg_link}")
    #         with open(egg_link) as f:
    #             print(f"連結內容：{f.read().strip()}")
    
    # 檢查 sys.path

if __name__ == "__main__":
    check_environment()
    # check_installation()
