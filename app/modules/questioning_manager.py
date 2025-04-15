import math
import numpy as np
from app.utils import text_processer as text
from app.modules.models_request.OpenAI_request import OpenAIRequest

class QuestioningManager():
    def __init__(self, subject, keypoints):
        self.subject = subject
        self.keypoints = keypoints
        self.model = OpenAIRequest()

        self.N = len(self.keypoints)
        self.T_min = 1 / (1 + math.log(self.N))
        self.T_max = 1 + (2 / (1 + math.log(self.N)))
        self.T = self._calculate_T()
        self.alpha = 1.0

        self.bases = [self.calculate_base(kp["Difficulty"],kp["Importance"])  for kp in self.keypoints]
        self.probabilitys = [self._calculate_probability(kp["Learning_Progress"],kp["Difficulty"])  for kp in self.keypoints]
        self.lrs = [self._calculate_learning_rate(kp["Learning_Progress"],kp["Difficulty"])  for kp in self.keypoints]

        self.overall_lr = sum(self.lrs)/self.N # 完成比例,0-100% (progress: 學習進度, 無上限)

    """ 抽選重點 """
    def _softmax(self, x):
        # Softmax 函數，T 是溫度參數
        x = np.array(x)
        e_x = np.exp((x - np.max(x)) / self.T)
        return e_x / e_x.sum(axis=0)

    def _select_index_from_softmax(self):
        # 根據 softmax 機率抽選一個 index

        # 計算每個元素的 base * p
        values = [self.bases[i] * self.probabilitys[i] for i in range(self.N)]

        # 使用 softmax 函數對計算結果進行轉換
        softmax_values = self._softmax(values)

        # 使用 numpy.random.choice 根據 softmax 機率抽選一個 index
        selected_index = np.random.choice(self.N, p=softmax_values)

        return selected_index


    """ 權重更新 """
    def _calculate_base(self, difficulty, importance):
        return math.log(1 + difficulty * importance)

    def _calculate_probability(self, progress, diff):
        progress = max(0,progress) # 若小於0則設為0
        return 1 / (1 + (progress / diff) ** self.alpha)
    
    def _calculate_learning_rate(self,progress,diff):
        if progress <= 0: # 若小於0則設為0%
            return 0.0
        elif progress >= 3*diff: # 若大於上限則為100%
            return 1.0
        else:
            return float(progress / (3*diff))

    def _calculate_T(self):
        self.T =  self.T_min + self.overall_lr * (self.T_max - self.T_min)


    """ 主流程函數 """
    def get_question(self):
        k_idx = self._select_index_from_softmax()
        keypoint_json = self.keypoints[k_idx]
        question_json = self.model.generate_question(self.subject, keypoint_json)
        return question_json
    
    def update_weights(self,answer_results):

        for result in answer_results:
            k_idx = result["Keypoints_Index"]
            is_Correct = result["is_Correct"]

            # update keypoint progress
            score  = 3 if is_Correct else -3
            self.keypoints[k_idx]['Learning_Progress'] += score

            # update overall lr, lr based on progress
            new_lr = self._calculate_learning_rate(self.keypoints[k_idx]['Learning_Progress'], self.keypoints[k_idx]['Difficulity'])
            self.overall_lr += (new_lr - self.lrs[k_idx]) / self.N
            self.lrs[k_idx] = new_lr

            # update prob based on progress
            self.probabilitys[k_idx] = self._calculate_probability(self.keypoints[k_idx]['Learning_Progress'], self.keypoints[k_idx]['Difficulity'])

        # update T based on overall_lr
        self._calculate_T()

        print("T: " + str(self.T))
        print("Overall lr: " + str(self.overall_lr))

        # return edited keypoints_json
        return self.keypoints

