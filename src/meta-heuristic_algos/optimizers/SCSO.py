import numpy as np
import matplotlib.pyplot as plt
from DataSet import DataSet

# 定義 Sand Cat Swarm Optimization (SCSO)
class SCSO:
    def __init__(self, obj_function, dim, lb, ub, num_cats, max_iter, f_type):
        self.obj_function = obj_function  # 目標函數
        self.dim = dim                    # 變數維度
        self.lb = np.array(lb)            # 下界
        self.ub = np.array(ub)            # 上界
        self.num_cats = num_cats          # 沙貓數量
        self.max_iter = max_iter          # 最大迭代次數
        self.f_type = f_type              # 連續/離散問題
        
        if self.f_type == "d":
            self.ub = np.append(self.ub[:], DataSet.NN_K)
            self.lb = np.append(self.lb[:], 1)
            self.dim += 1

        # 初始化沙貓位置
        self.cats = np.random.uniform(self.lb, self.ub, (self.num_cats, self.dim))
        self.best_cat = np.random.uniform(self.lb, self.ub, self.dim)
        self.best_score = np.inf

    def optimize(self):
        convergence_curve = []
        
        for t in range(self.max_iter):
            # 計算適應度並更新最佳沙貓
            for i in range(self.num_cats):
                fitness = self.obj_function(self.cats[i])
                if fitness < self.best_score:
                    self.best_score = fitness
                    self.best_cat = self.cats[i].copy()
            
            # 計算適應性參數 rG 和 R
            rG = 2 - (2 * t / self.max_iter)
            R = 2 * rG * np.random.rand() - rG
            
            # 更新位置
            for i in range(self.num_cats):
                r = rG * np.random.rand()
                theta = np.random.uniform(-np.pi, np.pi)  # 隨機角度
                if abs(R) <= 1:
                    # Exploitation: 逼近最佳位置
                    new_position = self.best_cat - r * np.random.rand() * (self.best_cat - self.cats[i]) * np.cos(theta)
                else:
                    # Exploration: 搜索新區域
                    new_position = r * (self.best_cat - np.random.rand() * self.cats[i])
                
                # 限制範圍
                if self.f_type == "d":
                    new_position[-1] = np.clip(new_position[-1], 1, DataSet.NN_K)
                    new_position[:-1] = np.clip(new_position[:-1], DataSet.param_LB, DataSet.param_UB)
                else:
                    self.cats[i] = np.clip(new_position, self.lb, self.ub)
            
            convergence_curve.append(self.best_score)
        
        return self.best_cat, self.best_score, convergence_curve, self.cats


class SCSOCONTROL:
    __name__ = "SCSO"
    def __init__(self, MAX_ITER, NUM_CATS, FUNCTION):
        self.MAX_ITER = MAX_ITER
        self.NUM_CATS = NUM_CATS

        self.UB = FUNCTION.ub
        self.LB = FUNCTION.lb
        self.DIM = FUNCTION.dim
        self.f = FUNCTION.func
        self.f_type = FUNCTION.f_type

    def Start(self):
        scso = SCSO(obj_function=self.f, dim=self.DIM, lb=self.LB, ub=self.UB, 
                    num_cats=self.NUM_CATS, max_iter=self.MAX_ITER, f_type=self.f_type)
        best_position, best_value, curve, cats = scso.optimize()
        
        if self.f_type == "d":
            return (cats, np.array(curve))
        else:
            return (cats, np.log10(curve))


if __name__ == '__main__':
    funcs_by_year = {
        "2021": ["F3", "F6", "F8", "F10"],
        "2022": ["F4", "F7", "F8", "F9"]
    }
    DIM = 10
    MAX_ITER = 500
    NUM_CATS = 30

    for year in funcs_by_year['CEC']:
        for func_name in funcs_by_year['CEC'][year]:
            function = DataSet.get_function(year, func_name, DIM)
            UB = function.ub
            LB = function.lb
            dim = function.dim
            f = function.func

            scso = SCSO(obj_function=f, dim=DIM, lb=LB, ub=UB, num_cats=NUM_CATS, max_iter=MAX_ITER)
            best_position, best_value, curve = scso.optimize()

            print(f"[CEC {year}-{func_name}] Best solution found:", best_position)
            print(f"[CEC {year}-{func_name}] Best fitness:", best_value)

            plt.figure(figsize=(8, 6))
            plt.plot(np.log10(curve), label=f"CEC {year} {func_name}")
            plt.xticks([i for i in range(0, MAX_ITER + 1, 50)])
            plt.xlabel("Iterations")
            plt.ylabel("Fitness Value (Log10)")
            plt.title(f"SCSO Convergence {year}-{func_name}-{DIM}D")
            plt.legend()
            plt.show()
