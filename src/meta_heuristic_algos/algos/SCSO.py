import os
import numpy as np
import matplotlib.pyplot as plt
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

class SCSO:
    def __init__(self, obj_function, dim, lb, ub, num_pop, max_iter, f_type, init_population=None):
        self.obj_function = obj_function
        self.dim = dim
        self.lb = np.array(lb)
        self.ub = np.array(ub)
        self.num_pop = num_pop
        self.max_iter = max_iter
        self.f_type = f_type
        
        if self.f_type == "d":
            self.ub = np.append(self.ub[:], DataSet.NN_K)
            self.lb = np.append(self.lb[:], 1)
            self.dim += 1

        if init_population is None:
            self.cats = np.random.uniform(self.lb, self.ub, (self.num_pop, self.dim))
        else:
            self.cats = init_population

        self.fitness = parallel_eval(self.obj_function, self.cats)
        best_idx = np.argmin(self.fitness)
        self.best_cat = self.cats[best_idx].copy()
        self.best_score = self.fitness[best_idx]

    def optimize(self):
        convergence_curve = []
        
        for t in range(self.max_iter):
            current_fitness = parallel_eval(self.obj_function, self.cats)
            min_idx = np.argmin(current_fitness)
            if current_fitness[min_idx] < self.best_score:
                self.best_score = current_fitness[min_idx]
                self.best_cat = self.cats[min_idx].copy()
            
            rG = 2 - (2 * t / self.max_iter)
            R = 2 * rG * np.random.rand() - rG
            
            for i in range(self.num_pop):
                r = rG * np.random.rand()
                theta = np.random.uniform(-np.pi, np.pi)
                if abs(R) <= 1:
                    new_position = self.best_cat - r * np.random.rand() * (self.best_cat - self.cats[i]) * np.cos(theta)
                else:
                    new_position = r * (self.best_cat - np.random.rand() * self.cats[i])
                
                if self.f_type == "d":
                    new_position[-1] = np.clip(new_position[-1], 1, DataSet.NN_K)
                    new_position[:-1] = np.clip(new_position[:-1], DataSet.param_LB, DataSet.param_UB)
                    self.cats[i] = new_position
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

    def start(self, init_population=None):
        scso = SCSO(obj_function=self.f, dim=self.DIM, lb=self.LB, ub=self.UB, 
                    num_pop=self.NUM_CATS, max_iter=self.MAX_ITER, f_type=self.f_type, init_population=init_population)
        best_position, best_value, curve, cats = scso.optimize()
        
        if self.f_type == "d":
            return (cats, np.array(curve))
        else:
            return (cats, np.log10(curve))

if __name__ == '__main__':
    pass