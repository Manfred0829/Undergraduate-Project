#!/usr/bin/env python3
"""
EasyOCR 修復測試腳本
此腳本測試修復後的 EasyOCR 處理功能，確保不會因為 matplotlib 問題而崩潰
"""

import os
import sys
import logging
import argparse
from PIL import Image
from app.modules.models_local.EasyOCR_local import EasyOCRLocal
from app.utils import media_processer as media

# 設置日誌
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("easyocr_test")

def test_easyocr_processing(image_path):
    """測試 EasyOCR 的行框處理功能"""
    # 檢查輸入文件是否存在
    if not os.path.exists(image_path):
        logger.error(f"找不到指定的圖片文件: {image_path}")
        return False
    
    # 檢查文件類型
    ext = os.path.splitext(image_path)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.pdf']:
        logger.error(f"不支持的文件類型: {ext}，只支持 JPG, JPEG, PNG 或 PDF")
        return False
    
    try:
        # 讀取圖片
        logger.info(f"嘗試讀取圖片: {image_path}")
        img = media.read_image_to_PIL(image_path)
        if img is None:
            logger.error("無法讀取圖片")
            return False
        logger.info(f"圖片讀取成功，尺寸: {img.size}")
        
        # 初始化 EasyOCR
        logger.info("初始化 EasyOCR...")
        easyocr = EasyOCRLocal()
        
        # 測試行框處理
        logger.info("開始處理圖片文字區域...")
        cropped_images = easyocr.processing_lines_bounding_box(img, draw_result=True)
        
        # 檢查結果
        logger.info(f"成功處理圖片，找到 {len(cropped_images)} 個文字區域")
        
        # 可選：保存部分結果用於檢查
        output_dir = os.path.join("test_output")
        os.makedirs(output_dir, exist_ok=True)
        
        for i, img in enumerate(cropped_images[:3]):  # 只保存前三個區域用於檢查
            output_path = os.path.join(output_dir, f"cropped_region_{i}.png")
            img.save(output_path)
            logger.info(f"保存了切割區域 {i} 到: {output_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"測試過程中發生錯誤: {str(e)}", exc_info=True)
        return False

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="測試修復後的 EasyOCR 處理功能")
    parser.add_argument("-i", "--image", required=True, 
                        help="測試用筆記圖片路徑")
    args = parser.parse_args()
    
    logger.info("===== 開始 EasyOCR 處理測試 =====")
    logger.info(f"圖片: {args.image}")
    
    success = test_easyocr_processing(args.image)
    
    if success:
        logger.info("===== 測試完成，EasyOCR 處理成功 =====")
        return 0
    else:
        logger.error("===== 測試完成，EasyOCR 處理失敗 =====")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 