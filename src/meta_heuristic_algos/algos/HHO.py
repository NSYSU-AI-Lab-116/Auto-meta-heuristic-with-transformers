import numpy as np
import math
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

def levy_flight(dim):
    beta = 1.5
    sigma = (math.gamma(1 + beta) * math.sin(math.pi * beta / 2) /
             (math.gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))) ** (1 / beta)
    u = 0.01 * np.random.randn(dim) * sigma
    v = np.random.randn(dim)
    step = u / (np.abs(v) ** (1 / beta))
    return step

class HHO:
    def __init__(self, obj_function, dim, lb, ub, num_hawks, max_iter, f_type, init_population=None):
        self.obj_function = obj_function
        self.dim = dim
        self.lb = np.array(lb)
        self.ub = np.array(ub)
        self.num_hawks = num_hawks
        self.max_iter = max_iter
        self.f_type = f_type
        self.parallel = Parallel(n_jobs=jobs_inner, backend="threading", verbose=0)

        if self.f_type == "d":
            self.ub = np.append(self.ub[:], DataSet.NN_K)
            self.lb = np.append(self.lb[:], 1)
            self.dim += 1

        if init_population is None:
            self.hawks = np.random.uniform(self.lb, self.ub, (self.num_hawks, self.dim))
        else:
            self.hawks = init_population

        fitnesses = parallel_eval(self.obj_function, self.hawks)
        best_idx = np.argmin(fitnesses)
        self.best_position = self.hawks[best_idx].copy()
        self.best_score = fitnesses[best_idx]
    
    def optimize(self):
        convergence_curve = []
        for t in range(self.max_iter):
            trial_hawks = np.zeros_like(self.hawks)
            for i in range(self.num_hawks):
                E0 = 2 * np.random.rand() - 1
                E = 2 * E0 * (1 - (t / self.max_iter))
                r = np.random.rand()
                J = 2 * (1 - np.random.rand())
                LF = levy_flight(self.dim)
                
                if abs(E) >= 1:
                    if r >= 0.5:
                        X_rand = self.hawks[np.random.randint(self.num_hawks)]
                        trial_hawks[i] = X_rand - r * np.abs(X_rand - 2 * r * self.hawks[i])
                    else:
                        trial_hawks[i] = self.best_position - np.mean(self.hawks, axis=0) - r * (self.lb + r * (self.ub - self.lb))
                else:
                    delta_X = self.best_position - self.hawks[i]
                    if r >= 0.5 and abs(E) >= 0.5:
                        trial_hawks[i] = delta_X - E * np.abs(J * self.best_position - self.hawks[i])
                    elif r >= 0.5 and abs(E) < 0.5:
                        trial_hawks[i] = self.best_position - E * np.abs(delta_X)
                    elif r < 0.5 and abs(E) >= 0.5:
                        Y = self.best_position - E * np.abs(J * self.best_position - self.hawks[i])
                        Z = Y + np.random.rand(self.dim) * LF
                        trial_hawks[i] = Z if self.obj_function(Z) < self.obj_function(Y) else Y
                    elif r < 0.5 and abs(E) < 0.5:
                        Y = self.best_position - E * np.abs(J * self.best_position - np.mean(self.hawks, axis=0))
                        Z = Y + np.random.rand(self.dim) * LF
                        trial_hawks[i] = Z if self.obj_function(Z) < self.obj_function(Y) else Y
                
                if self.f_type=='d':
                    trial_hawks[i][-1] = np.clip(trial_hawks[i][-1], 1, DataSet.NN_K)
                    trial_hawks[i][:-1] = np.clip(trial_hawks[i][:-1], DataSet.param_LB, DataSet.param_UB)
                else:
                    trial_hawks[i] = np.clip(trial_hawks[i], self.lb, self.ub)
            
            trial_fitnesses = np.array(
                self.parallel(delayed(safe_eval)(self.obj_function, ind, i)
                for i, ind in enumerate(trial_hawks)
            ))
            
            improved = trial_fitnesses < self.best_score
            self.hawks[improved] = trial_hawks[improved]
            
            current_best_idx = np.argmin(trial_fitnesses)
            if trial_fitnesses[current_best_idx] < self.best_score:
                self.best_score = trial_fitnesses[current_best_idx]
                self.best_position = trial_hawks[current_best_idx].copy()
            
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
    
    def start(self, init_population=None):
        hho = HHO(obj_function=self.f, dim=self.DIM, lb=self.LB, ub=self.UB, 
                  num_hawks=self.NUM_HAWKS, max_iter=self.MAX_ITER, f_type=self.f_type,
                  init_population=init_population)
        best_position, best_value, curve, hawks = hho.optimize()
        
        if self.f_type == "d":
            return (hawks, np.array(curve))
        else:
            return (hawks, np.log10(curve))

if __name__ == '__main__':
    pass