import unittest
import json
import os
import sys
import numpy as np

# 獲取當前文件的上層目錄（專案根目錄）
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.IO_processer import write_json, read_json
from utils.similarity_calculator import get_most_similar_index, get_similarity_pairs
import config

class TestJsonIO(unittest.TestCase):
    def setUp(self):
        """在測試開始前，設定測試檔案路徑"""
        self.test_file = os.path.join(config.get_project_root, "tests/test_data.json")

        """在測試前準備測試用的檔案與資料"""
        self.test_data = {"name": "Alice", "age": 25}
        self.target_vector = np.array([[1, 0]])
        self.data_vectors = np.array([[1, 0], [0, 1], [0.5, 0.5]])

    def test_write_and_read_json(self):
        """測試寫入與讀取 JSON"""
        test_data = {"name": "Alice", "age": 25}
        write_json(test_data, "tests/test_data.json")
        loaded_data = read_json("tests/test_data.json")
        self.assertEqual(test_data, loaded_data)

    def test_get_most_similar_index(self):
        """測試尋找最相似向量的索引"""
        index = get_most_similar_index(self.target_vector, self.data_vectors)
        self.assertEqual(index, 0)  # 目標向量 [1,0] 應該與 [1,0] 最相似

    def test_get_similarity_pairs(self):
        """測試計算所有組合的餘弦相似度"""
        similarities = get_similarity_pairs(self.target_vector, self.data_vectors)
        expected = np.array([[1.0, 0.0, 0.707]])
        np.testing.assert_almost_equal(similarities, expected, decimal=3)
        
    def tearDown(self):
        """測試結束後刪除測試檔案"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

if __name__ == '__main__':
    unittest.main()
