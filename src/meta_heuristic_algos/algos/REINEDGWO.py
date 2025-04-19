import os
import numpy as np
from joblib import Parallel, delayed
from src.meta_heuristic_algos.Config import Configs

DataSet = Configs.DataSet
jobs_inner = max(1, Configs.executer_num)

def safe_eval(fn, ind, idx):
    #np.random.seed(os.getpid() & 0xFFFF)
    return fn(ind, idx)

def parallel_eval(fn, pop):
    with Parallel(n_jobs=jobs_inner, backend="threading", verbose=0) as parallel:
        return np.array(
            parallel(delayed(safe_eval)(fn, ind, i)
            for i, ind in enumerate(pop)
        ))

class REIN_EDGWO:
    def __init__(self, obj_function, dim, lb, ub, num_pop, MAX_ITER, f_type, init_population=None):
        self.obj_function = obj_function
        self.dim = dim
        self.lb = np.array(lb)
        self.ub = np.array(ub)
        self.num_pop = num_pop
        self.MAX_ITER = MAX_ITER
        self.f_type = f_type

        if self.f_type == "d":
            self.ub = np.append(self.ub[:], DataSet.NN_K)
            self.lb = np.append(self.lb[:], 1)
            self.dim +=1

        if init_population is None:
            self.wolves = np.random.uniform(self.lb, self.ub, (self.num_pop, self.dim))
        else:
            self.wolves = init_population

        self.fitness = parallel_eval(self.obj_function, self.wolves)
        sorted_idx = np.argsort(self.fitness)
        self.alpha = self.wolves[sorted_idx[0]].copy()
        self.beta = self.wolves[sorted_idx[1]].copy()
        self.delta = self.wolves[sorted_idx[2]].copy()
        self.alpha_score = self.fitness[sorted_idx[0]]
        self.beta_score = self.fitness[sorted_idx[1]]
        self.delta_score = self.fitness[sorted_idx[2]]
        self.PreAlpha_score = np.inf

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
            current_fitness = parallel_eval(self.obj_function, self.wolves)
            sorted_idx = np.argsort(current_fitness)
            
            if current_fitness[sorted_idx[0]] < self.alpha_score:
                self.alpha_score = current_fitness[sorted_idx[0]]
                self.alpha = self.wolves[sorted_idx[0]].copy()
            if current_fitness[sorted_idx[1]] < self.beta_score:
                self.beta_score = current_fitness[sorted_idx[1]]
                self.beta = self.wolves[sorted_idx[1]].copy()
            if current_fitness[sorted_idx[2]] < self.delta_score:
                self.delta_score = current_fitness[sorted_idx[2]]
                self.delta = self.wolves[sorted_idx[2]].copy()

            a = 2 * np.exp(-t / self.MAX_ITER)
            for i in range(self.num_pop):
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

                if self.f_type == 'd':
                    self.wolves[i][-1] = np.clip(self.wolves[i][-1], 1, DataSet.NN_K)
                    self.wolves[i][:-1] = np.clip(self.wolves[i][:-1], DataSet.param_LB, DataSet.param_UB)
                else:
                    self.wolves[i] = np.clip(self.wolves[i], self.lb, self.ub)

            if (self.PreAlpha_score - self.alpha_score) < eps:
                strength = (self.ub - self.lb) * 0.05 * (1 - t / self.MAX_ITER)
                for i in range(self.num_pop):
                    if np.random.rand() < 0.1:
                        mutation = np.random.uniform(-1, 1, self.dim) * strength
                        self.wolves[i] = np.clip(self.wolves[i] + mutation, self.lb, self.ub)
            self.PreAlpha_score = self.alpha_score

            diversity = np.mean(np.std(self.wolves, axis=0))
            if diversity < 0.01 * np.mean(self.ub - self.lb):
                Reset_num = max(1, int(0.2 * self.num_pop))
                indices = np.random.choice(range(self.num_pop), size=Reset_num, replace=False)
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

    def start(self, init_population=None):
        gwo = REIN_EDGWO(obj_function=self.f, dim=self.DIM, lb=self.LB, ub=self.UB, 
                    num_pop=self.NUM_WOLVES, MAX_ITER=self.MAX_ITER, f_type=self.f_type, init_population=init_population)
        best_position, best_value, curve, wolves = gwo.optimize()
        
        if self.f_type == "d":
            return (wolves, np.array(curve))
        else:
            return (wolves, np.log10(curve))
    
if __name__ == '__main__':
    pass