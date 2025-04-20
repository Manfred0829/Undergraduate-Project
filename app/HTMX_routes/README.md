# HTMX 重構方案

本目錄包含使用 HTMX 技術對 `user_interface.html` 進行模組化重構的實現方案。

## 目錄結構

- `HTMX_templates/` - 包含所有 HTMX 模板片段
  - `layout.html` - 主佈局文件，包含頁面框架、頂部導航和側邊欄
  - `key_points.html` - 重點列表頁面片段
  - `outline.html` - 章節大綱頁面片段
  - `quiz.html` - 測驗系統頁面片段
  - `history.html` - 學習紀錄頁面片段
  - `upload.html` - 檔案上傳頁面片段

- `HTMX_routes/` - 包含處理 HTMX 請求的路由
  - `routes.py` - HTMX 相關的所有路由處理
  - `__init__.py` - 初始化文件，註冊路由

## 整合指南

### 1. 安裝 HTMX

在網頁的 `<head>` 部分添加 HTMX 庫：

```html
<script src="https://unpkg.com/htmx.org@1.9.4"></script>
```

### 2. 註冊 HTMX 路由

在 Flask 應用的入口點（通常是 `app/__init__.py`）中註冊 HTMX 路由：

```python
from app.HTMX_routes import register_htmx_routes

def create_app():
    app = Flask(__name__)
    # ... 其他設定 ...
    
    # 註冊 HTMX 路由
    register_htmx_routes(app)
    
    return app
```

### 3. 添加新導航選項

在原有應用的導航選單中添加一個選項，用於訪問 HTMX 版本：

```html
<a href="/htmx">HTMX 版本</a>
```

### 4. 漸進式整合

您可以選擇以下任一方式進行整合：

1. **並行策略**：保持原有 `user_interface.html` 不變，同時提供 HTMX 版本 (`/htmx` 路徑)，讓使用者可以選擇使用哪個版本。

2. **漸進式替換**：先在非關鍵頁面上部署 HTMX 版本，收集用戶反饋後，再逐步替換其他頁面。

3. **完全替換**：一次性替換所有原始頁面為 HTMX 版本（建議先在測試環境中完整測試）。

### 5. 整合考量

- **CSS 樣式一致性**：確保所有頁面的樣式保持一致，可考慮提取共用樣式到一個外部 CSS 文件。

- **JavaScript 兼容性**：確保原有的 JavaScript 功能與 HTMX 能夠和諧共存。

- **性能優化**：監控頁面載入時間和伺服器響應時間，確保 HTMX 請求不會對性能造成負面影響。

## 效益

- **提高可維護性**：每個功能模組都有獨立的檔案，便於維護。
- **減少重複代碼**：共用元素只需定義一次。
- **提高性能**：只加載需要的內容，減少初始載入時間。
- **漸進式增強**：HTMX 支持無 JavaScript 降級，提高可靠性。
- **更簡潔的開發流程**：前端開發人員可以專注於特定功能模組。

## 注意事項

1. 確保所有現有功能在重構後仍然正常工作。
2. 為每個新添加的頁面編寫測試用例。
3. 監控服務器負載，確保新的 HTMX 請求不會對系統造成過大壓力。
4. 在正式環境部署前，在測試環境中充分測試。 