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
                     for i, ind in enumerate(pop))
        )

class EDGWO:
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
        convergence_curve = [self.alpha_score]
        for t in range(self.max_iter):
            trial_pop = np.zeros_like(self.wolves)
            mean_pos = np.mean(self.wolves, axis=0)
            
            for i in range(self.num_pop):
                X1 = self.VectorComponentCalculation(2 - t*(2/self.max_iter), i, mean_pos, self.alpha)
                X2 = self.VectorComponentCalculation(2 - t*(2/self.max_iter), i, mean_pos, self.beta)
                X3 = self.VectorComponentCalculation(2 - t*(2/self.max_iter), i, mean_pos, self.delta)
                
                if (np.allclose(self.wolves[i], self.alpha) or 
                    np.allclose(self.wolves[i], self.beta) or 
                    np.allclose(self.wolves[i], self.delta)):
                    trial_pop[i] = (X1 + X2 + X3) / 3
                else:
                    if np.random.rand() < (0.5 * (1 - t / self.max_iter)):
                        trial_pop[i] = (X1 + X2 + X3) / 3
                    else:
                        l = -1 + 2 * np.random.rand()
                        trial_pop[i] = self.alpha + np.linalg.norm(self.alpha - self.wolves[i]) * np.exp(l) * np.cos(2 * np.pi * l)

                trial_pop[i] = np.clip(trial_pop[i], self.lb, self.ub)
                if self.f_type == 'd':
                    trial_pop[i][-1] = np.clip(trial_pop[i][-1], 1, DataSet.NN_K)
                    trial_pop[i][:-1] = np.clip(trial_pop[i][:-1], DataSet.param_LB, DataSet.param_UB)

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
        return (wolves, np.log10(curve)) if self.f_type != "d" else (wolves, np.array(curve))