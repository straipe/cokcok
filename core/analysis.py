import pandas as pd
import math
import ast
import csv
import numpy as np

import exception as ex
import utils as u
from constant import CONST



class SwingAnalysis:
    def __init__(self, file_path):
        self.file_path = file_path

    def cutData(self, all_data):
        return_data = []

        for data in all_data:
            sorted_column = data[CONST.ACCZ].sort_values(ascending=False)
            first_largest_value = sorted_column.iloc[0]
            second_largest_value = sorted_column.iloc[1]

            if second_largest_value > (first_largest_value * 9 / 10):
                second_index = data[data[CONST.ACCZ] == second_largest_value].index[0]
                first_index = data[data[CONST.ACCZ] == first_largest_value].index[0]
                if second_index > first_index:
                    max_index = second_index
                else:
                    max_index = data[CONST.ACCZ].idxmax()
            else:
                max_index = data[CONST.ACCZ].idxmax()

            start_index = max_index - CONST.SWING_BEFORE_IMPACT
            end_index = max_index + CONST.SWING_AFTER_IMPACT

            sliced_df = data.iloc[start_index:end_index].reset_index(drop=True)
            return_data.append(sliced_df)

        return return_data

    def normalize(self, all_data):
        return_data = []

        for data in all_data:
            result = data.copy()

            for feature_name in data.columns:
                max_value = data[feature_name].max()
                min_value = data[feature_name].min()

                result[feature_name] = (data[feature_name] - min_value) / (max_value - min_value)
            
            return_data.append(result)
        
        return return_data

    def windowing(self, all_data, size=CONST.SWING_WINDOW_SIZE):
        return_data = []

        for data in all_data:
            windowed_df = pd.DataFrame(columns=data.columns.tolist()) 

            for i in range(len(data) - size + 1):
                dic = {}

                for column_name in data.columns:
                    dic[column_name] = [data[column_name].iloc[i : i + size].tolist()]

                windowed_df = pd.concat([windowed_df, pd.DataFrame(dic)], ignore_index=True)

            return_data.append(windowed_df)

        return return_data
    
    def euclideanDistance(self, vector1, vector2):
        if len(vector1) != len(vector2):
            raise ValueError("벡터 길이가 같아야 합니다.")
        
        # 각 차원에서 차이를 제곱한 후 더한 값
        sum_of_squares = sum((v1 - v2) ** 2 for v1, v2 in zip(vector1, vector2))
        
        # 제곱근을 취한 결과가 두 벡터 간의 거리
        distance = math.sqrt(sum_of_squares)
        
        return distance

    def calDistance(self, avg, all_data):
        amount = len(all_data)
        return_dict = {}

        for feature_name in avg.columns:

            for i in range(len(avg)):
                return_dict[(i, feature_name)] = 0

            for data in all_data:
                for row in range(len(data)):
                    now = data.loc[row, feature_name]

                    c = []
                    c.append(self.euclideanDistance(now, avg.loc[row - 1, feature_name]) if row > 0 else len(now))
                    c.append(self.euclideanDistance(now, avg.loc[row, feature_name]))
                    c.append(self.euclideanDistance(now, avg.loc[row + 1, feature_name]) if row < (len(data) - 1) else len(now))

                    return_dict[(row, feature_name)] = return_dict[(row, feature_name)] + (min(c) / amount)

        return return_dict

    def analysis(self):
        # try:
            data = u.openStorageCSVFile(self.file_path)
            # TODO: data가 비었거나, 유효하지 않은 경우(예를 들어, 길이가 15 이하라면 이후 과정 진행이 불가하다) custom exception raise
            data = pd.read_csv(CONST.CURRENT_PATH + '/k fh.csv')

            added_data = u.addFeature([data])

            user_data = self.windowing(self.normalize(self.cutData(added_data)))

            ex_avg_path = CONST.CURRENT_PATH + '/ex_avg.csv'
            ex_avg_data = pd.read_csv(ex_avg_path)
            for col in ex_avg_data.columns.to_list():
                ex_avg_data[col] = ex_avg_data[col].apply(ast.literal_eval)
            
            distance = self.calDistance(ex_avg_data, user_data)

            ex_std_data = {}
            ex_std_path = CONST.CURRENT_PATH + '/ex_std.csv'
            with open(ex_std_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    key = (int(row[CONST.TIMESTAMP]), row[CONST.FEATURE])
                    value = float(row[CONST.VALUE])
                    ex_std_data[key] = value
            
            ex_dist_data = {}
            ex_dist_path = CONST.CURRENT_PATH + '/ex_dist.csv'
            with open(ex_dist_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    key = (int(row[CONST.TIMESTAMP]), row[CONST.FEATURE])
                    value = float(row[CONST.VALUE])
                    ex_dist_data[key] = value
            
            
            score = 0
            max = []
            for key in distance.keys():
                distsum = (distance[key] - ex_dist_data[key]) / ex_std_data[key]
                if distsum > 0:
                    score += distsum
                    max.append((key, distsum))
            
            self.score = score
            self.max = max

        # except Exception as e:
        #     return e

    def interpret(self):
        res_list = [0] * (CONST.SWING_BEFORE_IMPACT + CONST.SWING_AFTER_IMPACT)
        for tuple in self.max:
            print(tuple)
            for i in range(CONST.SWING_WINDOW_SIZE):
                res_list[tuple[0][0] + i] += tuple[1]
        
        self.res = res_list

a = SwingAnalysis('a')
print(a.analysis())
print(a.score)
print(a.max)
print(a.interpret())
print(a.res)

import matplotlib.pyplot as plt

# 막대 그래프 생성
plt.bar(range(len(a.res) - CONST.SWING_WINDOW_SIZE * 2), a.res[CONST.SWING_WINDOW_SIZE:-CONST.SWING_WINDOW_SIZE])

# 그래프에 제목과 축 레이블 추가
plt.title('Bar Chart of a List')
plt.xlabel('Index')
plt.ylabel('Value')

# 그래프 보이기
plt.show()