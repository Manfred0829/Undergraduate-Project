from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def get_most_similar_index(target, data):
    """
    計算目標向量與資料向量集合中最相似的向量索引。
    
    參數：
        target: array-like, 目標向量。
        data: array-like, 資料向量集合。
        
    返回：
        int: 最相似向量的索引 (標準Python整數類型)。
    """
    target_array = np.array(target).reshape(1, -1)
    data_array = np.array(data)
    similarities = cosine_similarity(target_array, data_array)
        
    # 找到相似度最高的索引
    most_similar_index = similarities.argmax()
    # 確保返回標準Python整數類型，而非np.int64
    return int(most_similar_index)

def get_similarity_pairs(target, data):
    """
    計算 target 與 data 所有組合的餘弦相似度。

    參數：
        target: 2D array-like, 每行為一個目標向量 (shape: [m, d])。
        data: 2D array-like, 每行為一個資料向量 (shape: [n, d])。

    返回：
        list: 所有組合的相似度 (標準Python列表和浮點數)。
    """
    target_array = np.array(target).reshape(1, -1)
    data_array = np.array(data)
    # 計算餘弦相似度
    similarities = cosine_similarity(target_array, data_array)
    # 確保返回標準Python列表和浮點數，而非NumPy類型
    return similarities.tolist()
