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

class BES:
    def __init__(self, obj_function, dim, lb, ub, num_par, max_iter, f_type, w=0.7, c1=1.5, c2=1.5, init_population=None):
        self.obj_function = obj_function
        self.dim = dim
        self.lb = np.array(lb)
        self.ub = np.array(ub)
        self.num_par = num_par
        self.max_iter = max_iter
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.f_type = f_type
        self.parallel = Parallel(n_jobs=jobs_inner, backend="threading", verbose=0)

        if self.f_type == "d":
            self.ub = np.append(self.ub[:], DataSet.NN_K)
            self.lb = np.append(self.lb[:], 1)
            self.dim+=1

        if init_population is None:
            self.particles = np.random.uniform(self.lb, self.ub, (self.num_par, self.dim))
        else:
            self.particles = init_population
            
        self.best_position = np.zeros((self.num_par, self.dim))
        self.energy = parallel_eval(self.obj_function, self.particles)
        self.best_energy = np.copy(self.energy)
        self.gbest_idx = np.argmin(self.energy)
        self.gbest_position = self.particles[self.gbest_idx].copy()
        self.gbest_energy = self.energy[self.gbest_idx]

    def optimize(self):
        convergence_curve = []
        for t in range(self.max_iter):
            trial_particles = np.zeros_like(self.particles)
            
            # 生成所有新位置
            for i in range(self.num_par):
                r1 = np.random.rand(self.dim)
                r2 = np.random.rand(self.dim)
                velocity = self.w * self.particles[i] + self.c1 * r1 * (self.best_position[i] - self.particles[i]) + self.c2 * r2 * (self.gbest_position - self.particles[i])
                trial_particles[i] = self.particles[i] + velocity
                
                if self.f_type == "d":
                    trial_particles[i][-1] = np.clip(trial_particles[i][-1], 1, DataSet.NN_K)
                    trial_particles[i][:-1] = np.clip(trial_particles[i][:-1], DataSet.param_LB, DataSet.param_UB)
                else:
                    trial_particles[i] = np.clip(trial_particles[i], self.lb, self.ub)

            # 并行评估所有新位置
            trial_energy = np.array(
                self.parallel(delayed(safe_eval)(self.obj_function, ind, i)
                for i, ind in enumerate(trial_particles))
            )

            # 更新粒子状态
            improved = trial_energy < self.energy
            self.particles[improved] = trial_particles[improved]
            self.energy[improved] = trial_energy[improved]
            
            # 更新个体和全局最优
            self.best_energy = np.where(trial_energy < self.best_energy, trial_energy, self.best_energy)
            self.best_position = np.where(improved[:, None], trial_particles, self.best_position)
            
            current_gbest_idx = np.argmin(self.energy)
            if self.energy[current_gbest_idx] < self.gbest_energy:
                self.gbest_energy = self.energy[current_gbest_idx]
                self.gbest_position = self.particles[current_gbest_idx].copy()

            convergence_curve.append(self.gbest_energy)

        return self.gbest_position, self.gbest_energy, convergence_curve, self.particles

class BESCONTROL:
    __name__ = "BES"
    def __init__(self,MAX_ITER, NUM_WOLVES,FUNCTION):
        self.MAX_ITER = MAX_ITER
        self.NUM_PARTICLES = NUM_WOLVES
        self.UB = FUNCTION.ub
        self.LB = FUNCTION.lb
        self.DIM= FUNCTION.dim
        self.f = FUNCTION.func
        self.f_type = FUNCTION.f_type

    def start(self, init_population=None):
        bes = BES(obj_function=self.f, dim=self.DIM, lb=self.LB, ub=self.UB, 
                    num_par=self.NUM_PARTICLES, max_iter=self.MAX_ITER, f_type=self.f_type, init_population=init_population)
        best_position, best_value, curve, particles = bes.optimize()
        
        if self.f_type == "d":
            return (particles, np.array(curve))
        else:
            return (particles, np.log10(curve))

if __name__ == '__main__':
    pass