import numpy as np
import math
import matplotlib.pyplot as plt

from DataSet import DataSet

def levy_flight(dim):
    beta = 1.5
    sigma = (math.gamma(1 + beta) * math.sin(math.pi * beta / 2) /
             (math.gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))) ** (1 / beta)
    u = 0.01 * np.random.randn(dim) * sigma
    v = np.random.randn(dim)
    step = u / (np.abs(v) ** (1 / beta))
    return step

class HHO:
    def __init__(self, obj_function, dim, lb, ub, num_hawks, max_iter, f_type):
        self.obj_function = obj_function
        self.dim = dim
        self.lb = np.array(lb)
        self.ub = np.array(ub)
        self.num_hawks = num_hawks
        self.max_iter = max_iter
        self.f_type = f_type

        if self.f_type == "d":
            self.ub = np.append(self.ub[:], DataSet.NN_K)
            self.lb = np.append(self.lb[:], 1)
            self.dim += 1
        
        # 初始化獵鷹位置
        self.hawks = np.random.uniform(self.lb, self.ub, (self.num_hawks, self.dim))
        self.best_position = None
        self.best_score = np.inf
    
    def optimize(self):
        convergence_curve = []
        for t in range(self.max_iter):
            
            # 計算適應度並找出最好的解（獵物）
            for i in range(self.num_hawks):
                fitness = self.obj_function(self.hawks[i])
                if fitness < self.best_score:
                    self.best_score = fitness
                    self.best_position = self.hawks[i].copy()
            
            E0 = 2 * np.random.rand() - 1  # 初始逃脫能量
            for i in range(self.num_hawks):
                E = 2 * E0 * (1 - (t / self.max_iter))  # 能量衰減
                r = np.random.rand()
                J = 2 * (1 - np.random.rand())
                LF = levy_flight(self.dim)
                
                if abs(E) >= 1:
                    if r >= 0.5:
                        X_rand = self.hawks[np.random.randint(self.num_hawks)]
                        self.hawks[i] = X_rand - r * np.abs(X_rand - 2 * r * self.hawks[i])
                    else:
                        self.hawks[i] = self.best_position - np.mean(self.hawks, axis=0) - r * (self.lb + r * (self.ub - self.lb))
                else:
                    delta_X = self.best_position - self.hawks[i]
                    if r >= 0.5 and abs(E) >= 0.5:
                        self.hawks[i] = delta_X - E * np.abs(J * self.best_position - self.hawks[i])
                    elif r >= 0.5 and abs(E) < 0.5:
                        self.hawks[i] = self.best_position - E * np.abs(delta_X)
                    elif r < 0.5 and abs(E) >= 0.5:
                        Y = self.best_position - E * np.abs(J * self.best_position - self.hawks[i])
                        Z = Y + np.random.rand(self.dim) * LF
                        self.hawks[i] = Z if self.obj_function(Z) < self.obj_function(Y) else Y
                    elif r < 0.5 and abs(E) < 0.5:
                        Y = self.best_position - E * np.abs(J * self.best_position - np.mean(self.hawks, axis=0))
                        Z = Y + np.random.rand(self.dim) * LF
                        self.hawks[i] = Z if self.obj_function(Z) < self.obj_function(Y) else Y
                
                if self.f_type=='d':# 邊界限制
                    self.hawks[i][-1] = np.clip(self.hawks[i][-1], 1, DataSet.NN_K)
                    self.hawks[i][:-1] = np.clip(self.hawks[i][:-1], DataSet.param_LB, DataSet.param_UB)
                else:
                    self.hawks[i] = np.clip(self.hawks[i], self.lb, self.ub)
            
            convergence_curve.append(self.best_score)
        
        return self.best_position, self.best_score, convergence_curve, self.hawks

class HHOCONTROL:
    __name__ = "HHO"
    def __init__(self, MAX_ITER, NUM_HAWKS, FUNCTION):
        self.MAX_ITER = MAX_ITER
        self.NUM_HAWKS = NUM_HAWKS
        
        self.UB = FUNCTION.ub
        self.LB = FUNCTION.lb
        self.DIM = FUNCTION.dim
        self.f = FUNCTION.func
        self.f_type = FUNCTION.f_type
    
    def Start(self):
        hho = HHO(obj_function=self.f, dim=self.DIM, lb=self.LB, ub=self.UB, 
                  num_hawks=self.NUM_HAWKS, max_iter=self.MAX_ITER, f_type=self.f_type)
        best_position, best_value, curve, hawks = hho.optimize()
        
        if self.f_type == "d":
            return (hawks, np.array(curve))
        else:
            return (hawks, np.log10(curve))

if __name__ == '__main__':

    funcs_by_year = DataSet.funcs_years
    
    MAX_ITER = 500
    NUM_HAWKS = 30
    DIM = 10
    
    for year in funcs_by_year['CEC']:
        for func_name in funcs_by_year['CEC'][year]:
            function = DataSet.get_function(year,func_name,DIM)
            UB = function.ub
            LB = function.lb
            f = function.func # 取得函式
            # 計算函式值 f([多個維度組成的陣列])   -> 例如 f([x,y])
            
            # 執行 HHO
            hho = HHO(obj_function=f, dim=DIM, lb=LB, ub=UB, num_hawks=NUM_HAWKS, max_iter=MAX_ITER)
            best_position, best_value, curve = hho.optimize()
            
            print(f"[CEC {year}-{func_name}] Best solution found:", best_position)
            print(f"[CEC {year}-{func_name}] Best fitness:", best_value)
            
            # 繪製收斂曲線
            plt.plot(np.log10(curve))
            plt.xlabel("Iterations")
            plt.ylabel("Fitness Value (Log10)")
            plt.title(f"HHO Convergence {year}-{func_name}-{DIM}D")
            plt.show()
