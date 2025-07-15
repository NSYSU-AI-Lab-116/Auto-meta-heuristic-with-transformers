import numpy as np
import pandas as pd
from scipy.stats import kruskal, linregress
import warnings

year = "2021"
warnings.filterwarnings("ignore", category=UserWarning, module="scipy.stats.stats")


a_data = np.load("/home/alvin/Hyper-heurisitc-J3C2025/research_workspace/auto-metaheuristic/exp_result/hh_result/data/de_curves.npy").mean(axis=0)


b_data_groups = []
for i in range(6):
    b_data_groups.append(np.load(f"/home/alvin/Hyper-heurisitc-J3C2025/research_workspace/auto-metaheuristic/exp_result/hh_result/data/{year}_curve_{i+1}.npy"))

print("--- 數據準備完成 ---")
print(f"A 數據組數: {len(a_data)}")
print(f"B 數據組數: ({len(b_data_groups)},{len(b_data_groups[0])})")



delta_values = []
for i, b_data in enumerate(b_data_groups):
    delta = b_data > a_data
    delta_values.append(delta)



def calculate_boolean_array_diff(arr1, arr2):
    arr1 = np.array(arr1, dtype=bool)
    arr2 = np.array(arr2, dtype=bool)
    hamming_distance = np.sum(arr1 != arr2)
    
    intersection = np.sum(arr1 & arr2)
    union = np.sum(arr1 | arr2)
    
    if union == 0:
        jaccard_similarity = 1.0
    else:
        jaccard_similarity = intersection / union
    
    jaccard_distance = 1 - jaccard_similarity
    
    
    diff_percentage = hamming_distance / len(arr1) * 100
    
    return {
        'hamming_distance': hamming_distance,
        'jaccard_distance': jaccard_distance,
        'jaccard_similarity': jaccard_similarity,
        'diff_percentage': diff_percentage,
        'total_length': len(arr1)
    }

result_array = []

for i,b in enumerate(delta_values[:-1]):
    for j, b_2 in enumerate(delta_values[i+1:]):
        result = calculate_boolean_array_diff(b, b_2)
        result_array.append(result["jaccard_similarity"])
        print(f"\n--- (B{i+1} vs B{j+i+2}) ---")
        print(f"漢明距離: {result['hamming_distance']}")
        print(f"差異百分比: {result['diff_percentage']:.1f}%")
        print(f"雅卡德相似度: {result['jaccard_similarity']:.3f}")
        print(f"雅卡德距離: {result['jaccard_distance']:.3f}")

print(f"\n--- 綜合結果 ---")
print(f"平均雅卡德距離：{np.mean(result_array)} ") 