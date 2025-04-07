from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def get_most_similar_index(target, data):

  similarities = cosine_similarity(target, data)

  # 找到相似度最高的索引
  most_similar_index = similarities.argmax()
  return most_similar_index

def get_similarity_pairs(target, data):
    """
    計算 target 與 data 所有組合的餘弦相似度。

    參數：
        target: 2D array-like, 每行為一個目標向量 (shape: [m, d])。
        data: 2D array-like, 每行為一個資料向量 (shape: [n, d])。

    返回：
        similarities: NumPy array (shape: [m, n])，所有組合的相似度。
    """
    # 計算餘弦相似度
    similarities = cosine_similarity(target, data)
    return similarities
