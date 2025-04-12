import numpy as np
import matplotlib.pyplot as plt

from src.meta_heuristic_algos.Config import Configs
DataSet = Configs.DataSet


# 定義 Grey Wolf Optimization (GWO)
class GWO:
    def __init__(self, obj_function, dim, lb, ub, num_wolves, max_iter, f_type, init_population=None):
        self.obj_function = obj_function
        self.dim = dim
        self.lb = np.array(lb)
        self.ub = np.array(ub)
        self.num_wolves = num_wolves
        self.max_iter = int(max_iter)
        self.f_type = f_type

        if self.f_type == "d":
            self.ub = np.append(self.ub[:], DataSet.NN_K)
            self.lb = np.append(self.lb[:], 1)
            self.dim += 1

        if init_population is None:
            self.wolves = np.random.uniform(self.lb, self.ub, (self.num_wolves, self.dim))
        else:
            self.wolves = init_population

        self.alpha, self.beta, self.delta = np.random.uniform(self.lb, self.ub, self.dim), np.random.uniform(self.lb, self.ub, self.dim), np.random.uniform(self.lb, self.ub, self.dim)
        self.alpha_score, self.beta_score, self.delta_score = np.inf, np.inf, np.inf

    def optimize(self):
        convergence_curve = []
        for t in range(self.max_iter):
            # 計算適應度並更新 α, β, δ
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

            # 更新狼群位置
            a = 2 - t * (2 / self.max_iter)  # 動態調整 a
            for i in range(self.num_wolves):

                # calcu;ating X1
                r1, r2 = np.random.rand(), np.random.rand()
                A1, C1 = 2 * a * r1 - a, 2 * r2
                D_alpha = abs(C1 * self.alpha - self.wolves[i])
                X1 = self.alpha - A1 * D_alpha

                # calculating X2
                r1, r2 = np.random.rand(), np.random.rand()
                A2, C2 = 2 * a * r1 - a, 2 * r2
                D_beta = abs(C2 * self.beta - self.wolves[i])
                X2 = self.beta - A2 * D_beta

                # calculating X3
                r1, r2 = np.random.rand(), np.random.rand()
                A3, C3 = 2 * a * r1 - a, 2 * r2
                D_delta = abs(C3 * self.delta - self.wolves[i])
                X3 = self.delta - A3 * D_delta

                self.wolves[i] = (X1 + X2 + X3) / 3

                if self.f_type =='d':# 限制範圍
                    self.wolves[i][:-1] = np.clip(self.wolves[i][:-1], 1, DataSet.NN_K)
                    self.wolves[i][-1] = np.clip(self.wolves[i][-1], DataSet.param_LB, DataSet.param_UB)
                else:
                    self.wolves[i] = np.clip(self.wolves[i], self.lb, self.ub)

            convergence_curve.append(self.alpha_score)
        
        return self.alpha, self.alpha_score, convergence_curve, self.wolves
    

class GWOCONTROL:
    __name__ = "GWO"
    def __init__(self, MAX_ITER, NUM_WOLVES, FUNCTION):
        self.MAX_ITER = MAX_ITER
        self.NUM_WOLVES = NUM_WOLVES
        self.UB = FUNCTION.ub
        self.LB = FUNCTION.lb
        self.DIM = FUNCTION.dim
        self.f = FUNCTION.func
        self.f_type = FUNCTION.f_type

    def start(self, init_population=None):
        gwo = GWO(obj_function=self.f, dim=self.DIM, lb=self.LB, ub=self.UB, 
                  num_wolves=self.NUM_WOLVES, max_iter=self.MAX_ITER, f_type=self.f_type,
                  init_population=init_population)
        best_position, best_value, curve, wolves = gwo.optimize()
        
        if self.f_type == "d":
            return (wolves, np.array(curve))
        else:
            return (wolves, np.log10(curve))


if __name__ == '__main__':
    pass