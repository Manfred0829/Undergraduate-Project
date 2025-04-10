#!/usr/bin/env python3
"""
筆記處理測試腳本
此腳本用於測試筆記上傳和處理流程，模擬網頁上傳筆記後的處理過程
"""

import os
import sys
import logging
import argparse
from app.services import main_processer
from app.utils import text_processer as text, media_processer as media

# 設置日誌
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("note_processing_test")

def setup_test_environment(subject):
    """準備測試環境，確保必要的目錄存在"""
    # 建立 data_upload 目錄
    upload_dir = os.path.join("app", "data_upload", subject, "notes")
    os.makedirs(upload_dir, exist_ok=True)
    
    # 建立 data_server 目錄
    server_dir = os.path.join("app", "data_server", subject, "notes")
    os.makedirs(server_dir, exist_ok=True)
    
    logger.info(f"測試環境準備完畢，目錄結構已創建: {upload_dir}, {server_dir}")
    
    return upload_dir, server_dir

def test_processing_note(subject, image_path):
    """測試筆記處理功能"""
    # 檢查輸入文件是否存在
    if not os.path.exists(image_path):
        logger.error(f"找不到指定的圖片文件: {image_path}")
        return False
    
    # 檢查文件類型
    ext = os.path.splitext(image_path)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.pdf']:
        logger.error(f"不支持的文件類型: {ext}，只支持 JPG, JPEG, PNG 或 PDF")
        return False
    
    # 準備測試環境
    upload_dir, server_dir = setup_test_environment(subject)
    
    # 測試讀取圖片
    logger.info(f"嘗試讀取圖片: {image_path}")
    img = media.read_image_to_PIL(image_path)
    if img is None:
        logger.error("無法讀取圖片")
        return False
    logger.info(f"圖片讀取成功，尺寸: {img.size}")

    try:
        # 測試筆記處理
        logger.info("開始執行筆記處理測試...")
        result = main_processer.processing_note(subject, image_path)
        
        if not result["success"]:
            logger.error(f"筆記處理失敗: {result.get('error', '未知錯誤')}")
            return False
            
        logger.info(f"筆記處理成功，輸出路徑: {result.get('output_path')}")
        
        # 檢查產生的JSON
        output_path = result.get('output_path')
        if os.path.exists(output_path):
            processed_data = text.read_json(output_path)
            logger.info(f"成功讀取處理結果，包含 {len(processed_data)} 個筆記重點")
            
            # 顯示部分結果
            if processed_data:
                for i, item in enumerate(processed_data[:3]):  # 只顯示前3個結果
                    logger.info(f"重點 #{i+1}:")
                    logger.info(f"  標題: {item.get('Title', '無標題')}")
                    logger.info(f"  內容: {item.get('Content', '無內容')[:100]}...")
                    logger.info(f"  對應講義ID: {item.get('Keypoint_id', '無對應ID')}")
            
            return True
        else:
            logger.error(f"輸出文件不存在: {output_path}")
            return False
            
    except Exception as e:
        logger.error(f"測試過程中發生錯誤: {str(e)}", exc_info=True)
        return False

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="測試筆記處理功能")
    parser.add_argument("-s", "--subject", required=True, 
                        help="科目名稱")
    parser.add_argument("-i", "--image", required=True, 
                        help="筆記圖片路徑")
    args = parser.parse_args()
    
    logger.info("===== 開始筆記處理測試 =====")
    logger.info(f"科目: {args.subject}")
    logger.info(f"圖片: {args.image}")
    
    success = test_processing_note(args.subject, args.image)
    
    if success:
        logger.info("===== 測試完成，處理成功 =====")
        return 0
    else:
        logger.error("===== 測試完成，處理失敗 =====")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 