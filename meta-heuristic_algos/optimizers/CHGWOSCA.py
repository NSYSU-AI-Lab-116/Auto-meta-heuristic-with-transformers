import numpy as np
import matplotlib.pyplot as plt
from DataSet import DataSet

class CHGWOSCA:
    def __init__(self, obj_function, dim, lb, ub, num_wolves, max_iter, f_type):
        self.obj_function = obj_function  
        self.dim = dim
        self.lb = np.array(lb)
        self.ub = np.array(ub)
        self.num_wolves = num_wolves
        self.max_iter = max_iter
        self.f_type = f_type

        if self.f_type == "d":
            self.ub = np.append(self.ub[:], DataSet.NN_K)
            self.lb = np.append(self.lb[:], 1)
            self.dim+=1

        self.wolves = np.random.uniform(self.lb, self.ub, (self.num_wolves, self.dim))
        self.alpha, self.beta, self.delta = np.random.uniform(self.lb, self.ub, self.dim),np.random.uniform(self.lb, self.ub, self.dim),np.random.uniform(self.lb, self.ub, self.dim)
        self.alpha_score, self.beta_score, self.delta_score = np.inf, np.inf, np.inf

    def optimize(self):
        convergence_curve = []
        for t in range(self.max_iter):
            # 更新 Alpha Beta Delta
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

            a = 2 - t * (2 / self.max_iter)
            w = t / self.max_iter # dynamic adjustment

            # 更新所有狼的位置
            for i in range(self.num_wolves):
                # --- GWO 更新公式 ---
                r1, r2 = np.random.rand(), np.random.rand() 
                A1, C1 = 2 * a * r1 - a, 2 * r2
                D_alpha = abs(C1 * self.alpha - self.wolves[i])
                X1 = self.alpha - A1 * D_alpha

                r1, r2 = np.random.rand(), np.random.rand()
                A2, C2 = 2 * a * r1 - a, 2 * r2
                D_beta = abs(C2 * self.beta - self.wolves[i])
                X2 = self.beta - A2 * D_beta

                r1, r2 = np.random.rand(), np.random.rand()
                A3, C3 = 2 * a * r1 - a, 2 * r2
                D_delta = abs(C3 * self.delta - self.wolves[i])
                X3 = self.delta - A3 * D_delta

                X_gwo = (X1 + X2 + X3) / 3

                # --- SCA 更新公式 ---
                r1_sca, r2_sca = np.random.rand(), np.random.rand()
                r3_sca, r4_sca = np.random.rand(), np.random.rand()
                if r4_sca < 0.5:
                    X_sca = self.wolves[i] + r1_sca * np.sin(r2_sca) * abs(r3_sca * self.alpha - self.wolves[i])
                else:
                    X_sca = self.wolves[i] + r1_sca * np.cos(r2_sca) * abs(r3_sca * self.alpha - self.wolves[i])

                # 混合
                X_new = w * X_gwo + (1-w) * X_sca

                if self.f_type == "d": #邊界處理
                    X_new[-1] = np.clip(X_new[-1], 1, DataSet.NN_K)
                    X_new[:-1] = np.clip(X_new[:-1], DataSet.param_LB, DataSet.param_UB) 
                else:
                    X_new = np.clip(X_new, self.lb, self.ub)
                self.wolves[i] = X_new

            convergence_curve.append(self.alpha_score)

        return self.alpha, self.alpha_score, convergence_curve, self.wolves


class CHGWOSCACONTROL:
    __name__ = "CHGWOSCA"
    def __init__(self,MAX_ITER, NUM_WOLVES, FUNCTION):
        self.MAX_ITER = MAX_ITER
        self.NUM_WOLVES = NUM_WOLVES
        
        self.UB = FUNCTION.ub
        self.LB = FUNCTION.lb
        self.DIM= FUNCTION.dim
        self.f = FUNCTION.func
        self.f_type = FUNCTION.f_type

    def Start(self):
        gwo = CHGWOSCA(obj_function=self.f, dim=self.DIM, lb=self.LB, ub=self.UB, 
                    num_wolves=self.NUM_WOLVES, max_iter=self.MAX_ITER, f_type=self.f_type)
        best_position, best_value, curve, wolves = gwo.optimize()
        
        """ print("Best solution found:", best_position)
        print("Best fitness:", best_value) """

        if self.f_type == "d":
            return (wolves, np.array(curve))
        else:
            return (wolves, np.log10(curve))




if __name__ == '__main__':

    funcs_by_year = DataSet.funcs_years

    # 設定參數
    MAX_ITER = 500
    NUM_WOLVES = 30
    DIM = 10

    # CEC 函式呼叫方法  
    for year in funcs_by_year['CEC']:
        for func_name in funcs_by_year['CEC'][year]:
            function = DataSet.get_function(year,func_name,DIM)  # 取得CEC Year年度，維度為 DIM 之 F1 函式的資訊
            UB = function.ub
            LB = function.lb
            f = function.func # 取得函式
            # 計算函式值 f([多個維度組成的陣列])   -> 例如 f([x,y])

    
            # 執行 GWO
            gwo = CHGWOSCA(obj_function=f, dim=DIM, lb=LB, ub=UB, num_wolves=NUM_WOLVES, max_iter=MAX_ITER)
            best_position, best_value, curve = gwo.optimize()

            print(f"[CEC {year}-{func_name}] Best solution found:", best_position)
            print(f"[CEC {year}-{func_name}] Best fitness:", best_value)

            # 繪製收斂曲線
            plt.plot(np.log10(curve))
            plt.xlabel("Iterations")
            plt.ylabel("Fitness Value (Log10)")
            plt.title(f"CH-GWOSCA Convergence {year}-{func_name}-{DIM}D")
            plt.show()
