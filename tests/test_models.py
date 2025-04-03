import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import concurrent.futures
import time

# 獲取當前文件的上層目錄（專案根目錄）
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.models_request.Gemini_request import GeminiRequest
from modules.models_request.OpenAI_request import OpenAIRequest
'''
class TestGeminiRequest(unittest.TestCase):

    def setUp(self):
        """初始化測試環境"""
        self.gemini = GeminiRequest()

    def test_singleton(self):
        """測試單例模式：不同變數應指向同一個物件"""
        gemini2 = GeminiRequest()
        self.assertIs(self.gemini, gemini2)  # 確保是同一個實例

    @patch("config.get_env_variable", return_value="FAKE_API_KEY")
    @patch("google.generativeai.GenerativeModel")
    def test_initialize(self, mock_model, mock_config):
        """測試初始化是否正確"""
        self.gemini.initialize()
        mock_config.assert_called_once_with("GOOGLE_API_KEY")  # 確保 API 金鑰有被讀取
        self.assertIsNotNone(self.gemini.model)  # model 不應該是 None
        self.assertTrue(self.gemini._initialized)  # 應該標記為已初始化

    @patch.object(GeminiRequest, "model")
    def test_gemini_request_success(self, mock_model):
        """測試 Gemini_Request 成功回應"""
        mock_response = MagicMock()
        mock_response.text = "Mocked response"
        mock_model.generate_content.return_value = mock_response

        result = self.gemini.Gemini_Request("Hello", "Test")
        self.assertEqual(result, "Mocked response")  # 確保回傳值正確

    @patch.object(GeminiRequest, "model")
    def test_gemini_request_timeout(self, mock_model):
        """測試請求超時機制"""
        mock_model.generate_content.side_effect = concurrent.futures.TimeoutError

        with self.assertRaises(RuntimeError) as cm:
            self.gemini.Gemini_Request("Hello", "Test", max_retries=3, timeout=2)

        self.assertEqual(str(cm.exception), "⛔ 超過最大重試次數，請求失敗")  # 確保超時錯誤處理

    @patch.object(GeminiRequest, "model")
    def test_gemini_request_exception_handling(self, mock_model):
        """測試請求發生異常時的錯誤處理"""
        mock_model.generate_content.side_effect = ValueError("Fake error")

        with self.assertRaises(RuntimeError) as cm:
            self.gemini.Gemini_Request("Hello", "Test", max_retries=3)

        self.assertEqual(str(cm.exception), "⛔ 超過最大重試次數，請求失敗")  # 確保異常處理機制
'''

if __name__ == "__main__":
    # unittest.main()

    #gemini = GeminiRequest()
    #print(gemini.generate_content("Testing LLM response: Give me randome content formated in json formate",return_json=True))
    openai = OpenAIRequest()
    print(openai.generate_content("Testing LLM response: Give me randome content formated in json formate",return_json=True,max_retries=1))