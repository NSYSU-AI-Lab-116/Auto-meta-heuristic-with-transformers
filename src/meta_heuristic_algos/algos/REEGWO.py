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

class REEGWO:
    def __init__(self, obj_function, dim, lb, ub, num_pop, max_iter, f_type, init_population=None):
        self.obj_function = obj_function  
        self.dim = dim
        self.lb = np.array(lb)
        self.ub = np.array(ub)
        self.num_pop = num_pop
        self.max_iter = max_iter
        self.f_type = f_type
        self.parallel = Parallel(n_jobs=jobs_inner, backend="threading", verbose=0)

        if self.f_type == "d":
            self.ub = np.append(self.ub[:], DataSet.NN_K)
            self.lb = np.append(self.lb[:], 1)
            self.dim+=1

        if init_population is None:
            self.wolves = np.random.uniform(self.lb, self.ub, (self.num_pop, self.dim))
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
            w_alpha, w_beta, w_delta = 0.5, 0.3, 0.2

            for i in range(self.num_pop):
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

                X_new = w_alpha * X1 + w_beta * X2 + w_delta * X3

                if self.f_type =='d':  
                    X_new[-1] = np.clip(X_new[-1], 1, DataSet.NN_K)
                    X_new[:-1] = np.clip(X_new[:-1], DataSet.param_LB, DataSet.param_UB)
                else:
                    X_new = np.clip(X_new, self.lb, self.ub)
                trial_pop[i] = X_new

            trial_fitness = np.array(
                self.parallel(delayed(safe_eval)(self.obj_function, ind, i)
                for i, ind in enumerate(trial_pop))
            )

            improved = trial_fitness < self.fitness
            self.wolves[improved] = trial_pop[improved]
            self.fitness[improved] = trial_fitness[improved]

            best_idx = np.argmin(self.fitness)
            self.alpha = self.wolves[best_idx].copy()
            self.alpha_score = self.fitness[best_idx]
            convergence_curve.append(self.alpha_score)

        return self.alpha, self.alpha_score, convergence_curve, self.wolves

class REEGWOCONTROL:
    __name__ = "REEGWO"
    def __init__(self,MAX_ITER, NUM_WOLVES, FUNCTION):
        self.MAX_ITER = MAX_ITER
        self.NUM_WOLVES = NUM_WOLVES
        self.UB = FUNCTION.ub
        self.LB = FUNCTION.lb
        self.DIM= FUNCTION.dim
        self.f = FUNCTION.func
        self.f_type = FUNCTION.f_type

    def start(self, init_population=None):
        gwo = REEGWO(obj_function=self.f, dim=self.DIM, lb=self.LB, ub=self.UB, 
                    num_pop=self.NUM_WOLVES, max_iter=self.MAX_ITER, f_type=self.f_type, init_population=init_population)
        best_position, best_value, curve, wolves = gwo.optimize()
        
        if self.f_type == "d":
            return (wolves, np.array(curve))
        else:
            return (wolves, np.log10(curve))

if __name__ == '__main__':
    pass