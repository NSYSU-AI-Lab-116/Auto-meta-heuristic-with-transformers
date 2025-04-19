""" GWO (Grey Wolf Optimization) algorithm implementation """
import numpy as np
import os
from joblib import Parallel, delayed
from src.meta_heuristic_algos.Config import Configs
DataSet = Configs.DataSet

jobs_inner = max(1, Configs.executer_num)

def safe_eval(fn, ind, idx):
    # ensure different seed
    #np.random.seed(os.getpid() & 0xFFFF)
    return fn(ind, idx)

def parallel_eval(fn, pop):
    with Parallel(n_jobs=jobs_inner, backend="threading", verbose=0) as parallel:
        return np.array(
            parallel(delayed(safe_eval)(fn, ind, i)
                     for i, ind in enumerate(pop))
        )

class GWO:
    def __init__(self, obj_function, dim, lb, ub, num_wolves, max_iter, f_type, init_population=None):
        self.obj_function = obj_function
        self.dim = dim
        self.lb = np.array(lb)
        self.ub = np.array(ub)
        self.num_wolves = num_wolves
        self.max_iter = int(max_iter)
        self.f_type = f_type
        self.parallel = Parallel(n_jobs=jobs_inner, backend="threading", verbose=0)

        if self.f_type == "d":
            self.ub = np.append(self.ub[:], DataSet.NN_K)
            self.lb = np.append(self.lb[:], 1)
            self.dim += 1

        if init_population is None:
            self.wolves = np.random.uniform(self.lb, self.ub, (self.num_wolves, self.dim))
        else:
            self.wolves = init_population

        self.fitness = parallel_eval(self.obj_function, self.wolves)
        best_idx = np.argmin(self.fitness)
        self.alpha = self.wolves[best_idx].copy()
        self.alpha_score = self.fitness[best_idx]
        self.beta = self.wolves[np.argsort(self.fitness)[1]].copy()
        self.beta_score = self.fitness[np.argsort(self.fitness)[1]]
        self.delta = self.wolves[np.argsort(self.fitness)[2]].copy()
        self.delta_score = self.fitness[np.argsort(self.fitness)[2]]

    def optimize(self):
        convergence_curve = [self.alpha_score]
        for t in range(self.max_iter):
            trial_pop = np.zeros_like(self.wolves)
            a = 2 - t * (2 / self.max_iter)
            
            for i in range(self.num_wolves):
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

                trial_pop[i] = (X1 + X2 + X3) / 3
                trial_pop[i] = np.clip(trial_pop[i], self.lb, self.ub)
                if self.f_type == 'd':
                    trial_pop[i][:-1] = np.clip(trial_pop[i][:-1], 1, DataSet.NN_K)
                    trial_pop[i][-1] = np.clip(trial_pop[i][-1], DataSet.param_LB, DataSet.param_UB)

            trial_fitness = np.array(self.parallel(delayed(safe_eval)(self.obj_function, ind, i) for i, ind in enumerate(trial_pop)))
            
            improved = trial_fitness < self.fitness
            self.wolves[improved] = trial_pop[improved]
            self.fitness[improved] = trial_fitness[improved]
            
            best_idx = np.argmin(self.fitness)
            self.alpha = self.wolves[best_idx].copy()
            self.alpha_score = self.fitness[best_idx]
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