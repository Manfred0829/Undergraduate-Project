from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def get_most_similar_index(target, data, threshold=0.80, need_threshold=False):
    """
    計算目標向量與資料向量集合中最相似的向量索引。
    
    參數：
        target: array-like, 目標向量。
        data: array-like, 資料向量集合。
        threshold: float, 門檻值，預設為0.80。
        need_threshold: bool, 是否需要門檻值，預設為False。
    返回：
        int: 最相似向量的索引（若低於門檻則回傳 -1）。
    """
    target_array = np.array(target).reshape(1, -1)
    data_array = np.array(data)
    similarities = cosine_similarity(target_array, data_array)  # shape: (1, N)
    
    most_similar_index = similarities.argmax()
    most_similar_score = similarities[0][most_similar_index]

    if need_threshold and most_similar_score < threshold:
        return -1

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
