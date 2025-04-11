#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試講義上傳和處理流程
"""

import os
import sys
import json
import time
import shutil
import argparse
import logging
from flask import Flask
from app.services import main_processer
from app.utils import text_processer

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_test_environment(subject_name):
    """設置測試環境"""
    # 確保測試科目目錄存在
    upload_dir = os.path.join("app", "data_upload", subject_name, "lectures")
    server_dir = os.path.join("app", "data_server", subject_name, "lectures")
    
    # 創建目錄
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(server_dir, exist_ok=True)
    
    # 創建索引文件
    index_path = os.path.join(upload_dir, 'index.json')
    if not os.path.exists(index_path):
        text_processer.write_json([], index_path)
    
    logger.info(f"測試環境設置完成，科目: {subject_name}")

def test_lecture_processing(subject_name, pdf_path):
    """測試講義處理功能"""
    if not os.path.exists(pdf_path):
        logger.error(f"找不到PDF文件: {pdf_path}")
        return False
    
    # 檢查文件類型
    if not pdf_path.lower().endswith('.pdf'):
        logger.error(f"檔案必須為PDF格式: {pdf_path}")
        return False
    
    try:
        # 複製PDF到上傳目錄
        filename = os.path.basename(pdf_path)
        upload_path = os.path.join("app", "data_upload", subject_name, "lectures", filename)
        shutil.copy2(pdf_path, upload_path)
        logger.info(f"已複製檔案到上傳目錄: {upload_path}")
        
        # 測量處理時間
        start_time = time.time()
        
        # 調用處理函數
        result = main_processer.processing_lecture(subject_name, upload_path)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 輸出結果
        if result['success']:
            logger.info(f"講義處理成功! 處理時間: {processing_time:.2f}秒")
            logger.info(f"輸出檔案:")
            logger.info(f"- 講義結構: {result['output_path']}")
            logger.info(f"- 重點向量: {result['keypoints_path']}")
            logger.info(f"- 結構樹: {result['tree_path']}")
            return True
        else:
            logger.error(f"講義處理失敗: {result['error']}")
            return False
    
    except Exception as e:
        logger.exception(f"測試過程中發生錯誤: {str(e)}")
        return False

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='測試講義處理功能')
    parser.add_argument('--subject', type=str, default='測試科目', help='科目名稱')
    parser.add_argument('--pdf', type=str, required=True, help='PDF檔案路徑')
    
    args = parser.parse_args()
    
    # 設置測試環境
    setup_test_environment(args.subject)
    
    # 執行測試
    success = test_lecture_processing(args.subject, args.pdf)
    
    # 返回結果
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 