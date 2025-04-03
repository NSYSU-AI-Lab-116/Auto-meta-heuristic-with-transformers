import numpy as np
import matplotlib.pyplot as plt

from DataSet import DataSet

class REIN_EDGWO:
    def __init__(self, obj_function, dim, lb, ub, num_wolves, MAX_ITER, f_type):
        self.obj_function = obj_function  # 目標函數
        self.dim = dim                    # 變數維度
        self.lb = np.array(lb)            # 下界
        self.ub = np.array(ub)            # 上界
        self.num_wolves = num_wolves      # 狼群數量
        self.MAX_ITER = MAX_ITER          # 最大迭代次數
        self.f_type = f_type

        if self.f_type == "d":
            self.ub = np.append(self.ub[:], DataSet.NN_K)
            self.lb = np.append(self.lb[:], 1)
            self.dim+=1

        # 初始化狼群位置
        self.wolves = np.random.uniform(self.lb, self.ub, (self.num_wolves, self.dim))
        self.alpha, self.beta, self.delta = np.random.uniform(self.lb, self.ub, self.dim),np.random.uniform(self.lb, self.ub, self.dim),np.random.uniform(self.lb, self.ub, self.dim)
        self.alpha_score, self.beta_score, self.delta_score = np.inf, np.inf, np.inf

        # 突變判斷
        self.PreAlpha_score = np.inf

    # 基本運算
    def VectorComponentCalculation(self, a, index, Xm, targetlead):
        r1, r2 = np.random.rand(), np.random.rand()
        A, C = 2 * a * r1 - a, 2 * r2

        if A < 1: 
            D = abs(C * targetlead - self.wolves[index])
            return targetlead - A * D
        else:
            r3, r4 = np.random.rand(), np.random.rand()
            return targetlead - Xm - r3 * (self.lb + (self.ub-self.lb) * r4)

    def optimize(self):
        convergence_curve = []
        eps = 1e6
        for t in range(self.MAX_ITER):
            mean_pos = np.mean(self.wolves, axis=0)

            for i in range(self.num_wolves):
                fitness = self.obj_function(self.wolves[i])
                if fitness < self.alpha_score:
                    self.delta_score, self.delta = self.beta_score, self.beta.copy()
                    self.beta_score, self.beta = self.alpha_score, self.alpha.copy()
                    self.alpha_score, self.alpha = fitness, self.wolves[i].copy()
                elif fitness < self.beta_score:
                    self.delta_score, self.delta = self.beta_score, self.beta.copy()
                    self.beta_score, self.beta = fitness, self.wolves[i].copy()
                elif fitness < self.delta_score:
                    self.delta_score, self.delta = fitness, self.wolves[i].copy()

            a = 2 * np.exp(-t / self.MAX_ITER) # 改用指數衰減
            for i in range(self.num_wolves):
                X1 = self.VectorComponentCalculation(a, index=i, Xm=mean_pos, targetlead=self.alpha)
                X2 = self.VectorComponentCalculation(a, index=i, Xm=mean_pos, targetlead=self.beta)
                X3 = self.VectorComponentCalculation(a, index=i, Xm=mean_pos, targetlead=self.delta)
                if (np.allclose(self.wolves[i], self.alpha) or np.allclose(self.wolves[i], self.beta) or np.allclose(self.wolves[i], self.delta)):
                    self.wolves[i]=(X1 + X2 + X3) / 3
                else:
                    if np.random.rand() < (0.5 * (1 - t / self.MAX_ITER)):
                        self.wolves[i] = (X1 + X2 + X3) / 3
                    else:
                        r5 = np.random.rand()
                        l = -1 + 2 * r5
                        self.wolves[i] = self.alpha + np.linalg.norm(self.alpha - self.wolves[i]) * np.exp(l) * np.cos(2 * np.pi * l)

                # 限制範圍
                if self.f_type == 'd':
                    self.wolves[i][-1] = np.clip(self.wolves[i][-1], 1, DataSet.NN_K)
                    self.wolves[i][:-1] = np.clip(self.wolves[i][:-1], DataSet.param_LB, DataSet.param_UB)
                else:
                    self.wolves[i] = np.clip(self.wolves[i], self.lb, self.ub)
        
            # alpha改變量很小時
            if (self.PreAlpha_score - self.alpha_score) < eps:
                # 擾動(隨時間遞減)
                strength = (self.ub - self.lb) * 0.05 * (1 - t / self.MAX_ITER)
                for i in range(self.num_wolves):
                    if np.random.rand() < 0.1:  # 10% 對個體進行突變
                        mutation = np.random.uniform(-1, 1, self.dim) * strength
                        self.wolves[i] = np.clip(self.wolves[i] + mutation, self.lb, self.ub)
            self.PreAlpha_score = self.alpha_score

            # 多樣性過低 -> reset部分個體
            diversity = np.mean(np.std(self.wolves, axis=0))
            if diversity < 0.01 * np.mean(self.ub - self.lb):
                Reset_num = max(1, int(0.2 * self.num_wolves)) # 隨機選擇20%
                indices = np.random.choice(range(self.num_wolves), size=Reset_num, replace=False)
                for idx in indices:
                    self.wolves[idx] = np.random.uniform(self.lb, self.ub, self.dim)


                
            convergence_curve.append(self.alpha_score)
        return self.alpha, self.alpha_score, convergence_curve, self.wolves
    
class REINEDGWOCONTROL:
    __name__ = "REINEDGWO"
    def __init__(self,MAX_ITER, NUM_WOLVES,  FUNCTION):
        self.MAX_ITER = MAX_ITER
        self.NUM_WOLVES = NUM_WOLVES

        self.UB = FUNCTION.ub
        self.LB = FUNCTION.lb
        self.DIM= FUNCTION.dim
        self.f = FUNCTION.func
        self.f_type = FUNCTION.f_type

    def Start(self):
        gwo = REIN_EDGWO(obj_function=self.f, dim=self.DIM, lb=self.LB, ub=self.UB, 
                    num_wolves=self.NUM_WOLVES, MAX_ITER=self.MAX_ITER, f_type=self.f_type)
        best_position, best_value, curve, wolves = gwo.optimize()
        
        """ print("Best solution found:", best_position)
        print("Best fitness:", best_value) """
        if self.f_type == "d":
            return (wolves, np.array(curve))
        else:
            return (wolves, np.log10(curve))
    
if __name__ == '__main__':
    funcs_by_year = DataSet.funcs_years
    DIM = 10
    MAX_ITER = 500
    NUM_WOLVES = 30

    # CEC 函式呼叫方法  
    for year in funcs_by_year['CEC']:
        for func_name in funcs_by_year['CEC'][year]:
            function = DataSet.get_function(year,func_name,DIM) # 取得CEC Year年度，維度為 DIM 之 F1 函式的資訊
            UB = function.ub
            LB = function.lb
            dim= function.dim
            f = function.func # 取得函式
            # 計算函式值 f([多個維度組成的陣列])   -> 例如 f([x,y])



            # 設定參數
            
            # 執行 GWO
            gwo = REIN_EDGWO(obj_function=f, dim=DIM, lb=LB, ub=UB, num_wolves=NUM_WOLVES, max_iter=MAX_ITER)
            best_position, best_value, curve, _ = gwo.optimize()

            print(f"[CEC {year}-{func_name}] Best solution found:", best_position)
            print(f"[CEC {year}-{func_name}] Best fitness:", best_value)

            # 繪製收斂曲線
            plt.figure(figsize=(8, 6))
            plt.plot(np.log10(curve), label=f"CEC {year} {func_name}")
            plt.xticks([i for i in range(0, MAX_ITER + 1, 50)])
            plt.xlabel("Iterations")
            plt.ylabel("Fitness Value (Log10)")
            plt.title(f"REIN-EDGWO Convergence {year}-{func_name}-{DIM}D")
            plt.legend()
            plt.show()