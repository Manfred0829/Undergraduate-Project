# HTMX 版本測試伺服器

這個檔案用於快速啟動一個測試環境，以展示使用 HTMX 重構後的使用者介面。

## 使用方法

1. 確保已安裝所需的 Python 套件：

```bash
# 使用提供的需求文件安裝依賴
pip install -r htmx_requirements.txt
```

2. 執行測試伺服器：

```bash
python HTMX_run.py
```

3. 在瀏覽器中訪問：http://localhost:5000

## 可能遇到的問題與解決方案

1. **模板無法找到**：
   - 錯誤信息：`jinja2.exceptions.TemplateNotFound: HTMX_templates/layout_with_chart.html`
   - 解決方案：確保 app 目錄中包含 HTMX_templates 子目錄，且文件名稱正確

2. **無法連接到伺服器**：
   - 檢查防火牆設置，或嘗試將 host 參數從 0.0.0.0 改為 127.0.0.1
   
3. **圖表無法顯示**：
   - 確保使用的是 layout_with_chart.html，其中包含了對 Chart.js 的引用
   - 檢查瀏覽器控制台是否有 JavaScript 錯誤

## 主要功能

這個測試伺服器提供以下功能：

- 啟動一個獨立的 Flask 應用，專門用於 HTMX 版本的介面
- 載入並註冊 HTMX 相關的路由和模板
- 提供一個完整的使用者介面，展示使用 HTMX 重構後的效果
- 支援即時反饋和動態載入內容

## 注意事項

- 這個測試伺服器與主應用完全獨立，不會影響原始的使用者介面
- 使用的是開發模式 (`debug=True`)，不適合在生產環境中使用
- 修改 HTMX_templates 目錄下的模板文件或 HTMX_routes 目錄下的路由文件後，伺服器會自動重新載入

## 檔案結構

```
/
├── HTMX_run.py            # 主要啟動文件
├── htmx_requirements.txt  # 依賴包清單
├── app/
│   ├── HTMX_templates/    # HTMX 模板目錄
│   │   ├── layout_with_chart.html   # 主模板 (含 Chart.js)
│   │   ├── key_points.html          # 重點列表模板
│   │   ├── outline.html             # 章節大綱模板
│   │   ├── quiz.html                # 測驗系統模板
│   │   ├── history.html             # 學習紀錄模板
│   │   └── upload.html              # 上傳檔案模板
│   ├── HTMX_routes/       # HTMX 路由目錄
│   │   ├── __init__.py              # 初始化文件
│   │   ├── routes.py                # 路由定義
│   │   └── README.md                # 整合指南
```

## 整合到主應用

要將 HTMX 版本整合到主應用中，請參考 `app/HTMX_routes/README.md` 中的整合指南。 