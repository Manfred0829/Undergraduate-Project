# EasyOCR 線程問題修復指南

## 問題描述

在使用 macOS 系統上運行筆記處理功能時，程序突然崩潰並顯示以下錯誤：

```
NSInternalInconsistencyException: 'NSWindow should only be instantiated on the main thread!'
```

問題出現在 `app/modules/models_local/EasyOCR_local.py` 的 `_draw_lines_boxes` 函數中，當它嘗試使用 matplotlib 在非主線程中顯示圖像時發生崩潰。

## 原因分析

1. 在 macOS 上，GUI 相關操作（包括 matplotlib 的圖形顯示）必須在主線程上執行
2. 在處理筆記時，web 服務器在後台線程中執行 EasyOCR 處理
3. EasyOCR 處理中調用了 matplotlib 顯示功能，嘗試創建視窗
4. 這導致了線程安全問題，因為 matplotlib 嘗試在非主線程中創建視窗

## 解決方案

### 1. 移除 matplotlib 顯示功能

從 `_draw_lines_boxes` 函數中移除以下代碼：
```python
plt.imshow(pil_image)
plt.axis('off')  # 不顯示軸線
plt.show(block=False)  # 顯示圖片
```

### 2. 改為返回處理後的圖像

修改函數，使其返回標記後的圖像而不是顯示：
```python
def _draw_lines_boxes(self, pil_image, lines_boxes):
    # 複製一個新圖片，以免修改原始圖片
    pil_image = pil_image.copy()
    
    # 使用 PIL 的 ImageDraw 進行繪製
    draw = ImageDraw.Draw(pil_image)

    for box in lines_boxes:
        x1, y1, x2, y2 = box
        draw.rectangle([x1, y1, x2, y2], outline="red", width=3)  # 繪製紅色矩形框
    
    return pil_image
```

### 3. 更新引用處代碼

修改 `processing_lines_bounding_box` 函數適應這一變化：
```python
if draw_result:
    processed_image = self._draw_lines_boxes(pil_image, lines_box)
    # 如需保存處理後的圖像，可以在這裡添加保存代碼
```

### 4. 移除 matplotlib 導入

從文件頂部移除：
```python
import matplotlib.pyplot as plt
```

## 驗證修復

使用提供的測試腳本驗證修復是否有效：

```bash
python test_easyocr_fix.py -i <筆記圖片路徑>
```

如果測試成功，則修復有效。然後可以嘗試通過 web 界面正常上傳筆記。

## 注意事項

1. 此修復不會影響功能，只是移除了調試時的可視化顯示
2. 如果需要可視化檢查，可以將處理後的圖像保存到文件而不是顯示
3. 可以考慮增加配置選項，允許在調試模式下保存處理圖像 