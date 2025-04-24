import numpy as np

from src.meta_heuristic_algos.Config import Configs
DataSet = Configs.DataSet


# 定義 EDGWO
class EDGWO:
    def __init__(self, obj_function, dim, lb, ub, num_pop, max_iter, f_type, init_population=None):
        self.obj_function = obj_function  # 目標函數
        self.dim = dim                    # 變數維度
        self.lb = np.array(lb)            # 下界
        self.ub = np.array(ub)            # 上界
        self.num_pop = num_pop      # 狼群數量
        self.max_iter = max_iter          # 最大迭代次數
        self.f_type = f_type              # 連續/離散問題

        if self.f_type == "d":
            self.ub = np.append(self.ub[:], DataSet.NN_K)
            self.lb = np.append(self.lb[:], 1)
            self.dim+=1

        # 初始化狼群位置
        if init_population is None:
            self.wolves = np.random.uniform(self.lb, self.ub, (self.num_pop, self.dim))
        else:
            self.wolves = init_population

        self.alpha, self.beta, self.delta = np.random.uniform(self.lb, self.ub, self.dim),\
                                            np.random.uniform(self.lb, self.ub, self.dim),\
                                            np.random.uniform(self.lb, self.ub, self.dim)

        # 初始化狼群位置
        self.alpha_score, self.beta_score, self.delta_score = np.inf, np.inf, np.inf
    
    # 三種全局探索
    def VectorComponentCalculation(self, a, index, Xm, targetlead):
        r1, r2 = np.random.rand(), np.random.rand()
        A, C = 2 * a * r1 - a, 2 * r2

        if A < 1: 
            D = abs(C * targetlead - self.wolves[index])
            return targetlead - A * D
        else:
            r3, r4 = np.random.rand(), np.random.rand()
            return targetlead - Xm - r3 * (self.lb + (self.ub-self.lb) * r4)
            #return self.alpha - Xm - r3 * (self.lb + (self.ub-self.lb) * r4)
        
    def optimize(self):
        convergence_curve = []
        for t in range(self.max_iter):
            # 計算適應度並更新
            mean_pos = np.mean(self.wolves, axis=0)
            for i in range(self.num_pop):
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

            # 動態調整 (Elite vs. Ordinary)
            a = 2 - t * (2 / self.max_iter)

            for i in range(self.num_pop):

                """ # calcu;ating X1
                r1, r2 = np.random.rand(), np.random.rand()
                A1, C1 = 2 * a * r1 - a, 2 * r2
                D_alpha = abs(C1 * self.alpha - self.wolves[i])
                X1 = self.alpha - A1 * D_alpha """
                X1 = self.VectorComponentCalculation(a, index=i, Xm=mean_pos, targetlead=self.alpha)


                """ # calculating X2
                r1, r2 = np.random.rand(), np.random.rand()
                A2, C2 = 2 * a * r1 - a, 2 * r2
                D_beta = abs(C2 * self.beta - self.wolves[i])
                X2 = self.beta - A2 * D_beta """
                X2 = self.VectorComponentCalculation(a, index=i, Xm=mean_pos, targetlead=self.beta)

                """ # calculating X3
                r1, r2 = np.random.rand(), np.random.rand()
                A3, C3 = 2 * a * r1 - a, 2 * r2
                D_delta = abs(C3 * self.delta - self.wolves[i])
                X3 = self.delta - A3 * D_delta """
                X3 = self.VectorComponentCalculation(a, index=i, Xm=mean_pos, targetlead=self.delta)


                if (np.allclose(self.wolves[i], self.alpha) or np.allclose(self.wolves[i], self.beta) or np.allclose(self.wolves[i], self.delta)):
                    self.wolves[i]=(X1 + X2 + X3) / 3
                else:
                    if np.random.rand() < (0.5 * (1 - t / self.max_iter)):
                        self.wolves[i] = (X1 + X2 + X3) / 3
                    else:
                        r5 = np.random.rand()
                        l = -1 + 2 * r5
                        self.wolves[i] = self.alpha + np.linalg.norm(self.alpha - self.wolves[i]) * np.exp(l) * np.cos(2 * np.pi * l)

                if self.f_type== 'd':# 限制範圍
                    self.wolves[i][-1] = np.clip(self.wolves[i][-1], 1, DataSet.NN_K)
                    self.wolves[i][:-1] = np.clip(self.wolves[i][:-1], DataSet.param_LB, DataSet.param_UB)
                else:
                    self.wolves[i] = np.clip(self.wolves[i], self.lb, self.ub)

            convergence_curve.append(self.alpha_score)
        return self.alpha, self.alpha_score, convergence_curve, self.wolves

class EDGWOCONTROL:
    __name__ = "EDGWO"
    def __init__(self,MAX_ITER, NUM_WOLVES, FUNCTION=10):
        self.MAX_ITER = MAX_ITER
        self.NUM_WOLVES = NUM_WOLVES

        self.UB = FUNCTION.ub
        self.LB = FUNCTION.lb
        self.DIM= FUNCTION.dim
        self.f = FUNCTION.func
        self.f_type = FUNCTION.f_type

    def start(self, init_population=None):
        edgwo = EDGWO(obj_function=self.f, dim=self.DIM, lb=self.LB, ub=self.UB, 
                    num_pop=self.NUM_WOLVES, max_iter=self.MAX_ITER, f_type=self.f_type, init_population=init_population)
        best_position, best_value, curve, wolves = edgwo.optimize()
        
        """ print("Best solution found:", best_position)
        print("Best fitness:", best_value) """

        if self.f_type == "d":
            return (wolves, np.array(curve))
        else:
            return (best_position, best_value, wolves, curve)


if __name__ == '__main__':
    pass
