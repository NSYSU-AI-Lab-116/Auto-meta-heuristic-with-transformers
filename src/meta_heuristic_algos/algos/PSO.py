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

class PSO:
    def __init__(self, obj_function, dim, lb, ub, num_par, max_iter, f_type, init_population=None):
        self.obj_function = obj_function
        self.dim = dim
        self.lb = np.array(lb)
        self.ub = np.array(ub)
        self.num_par = num_par
        self.max_iter = max_iter
        self.f_type = f_type
        self.w = 0.7
        self.c1 = 2
        self.c2 = 2
        self.parallel = Parallel(n_jobs=jobs_inner, backend="threading", verbose=0)

        if self.f_type == "d":
            self.ub = np.append(self.ub[:], DataSet.NN_K)
            self.lb = np.append(self.lb[:], 1)
            self.dim += 1

        if init_population is None:
            self.particles = np.random.uniform(self.lb, self.ub, (self.num_par, self.dim))
        else:
            self.particles = init_population

        self.velocities = np.random.uniform(-abs(self.ub - self.lb), abs(self.ub - self.lb), (self.num_par, self.dim))
        self.pbest = self.particles.copy()
        self.pbest_scores = parallel_eval(self.obj_function, self.particles)
        self.gbest_idx = np.argmin(self.pbest_scores)
        self.gbest = self.particles[self.gbest_idx].copy()
        self.gbest_score = self.pbest_scores[self.gbest_idx]
    
    def optimize(self):
        convergence_curve = []
        for t in range(self.max_iter):
            # 生成所有新位置
            trial_particles = np.zeros_like(self.particles)
            for i in range(self.num_par):
                r1, r2 = np.random.rand(self.dim), np.random.rand(self.dim)
                cognitive = self.c1 * r1 * (self.pbest[i] - self.particles[i])
                social = self.c2 * r2 * (self.gbest - self.particles[i])
                self.velocities[i] = self.w * self.velocities[i] + cognitive + social
                trial_particles[i] = self.particles[i] + self.velocities[i]

                # 邊界處理
                if self.f_type =="d":
                    trial_particles[i][-1] = np.clip(trial_particles[i][-1], 1, DataSet.NN_K)
                    trial_particles[i][:-1] = np.clip(trial_particles[i][:-1], DataSet.param_LB, DataSet.param_UB)
                else:
                    trial_particles[i] = np.clip(trial_particles[i], self.lb, self.ub)

            # 并行評估所有粒子
            trial_scores = np.array(
                self.parallel(delayed(safe_eval)(self.obj_function, ind, i)
                for i, ind in enumerate(trial_particles)
            ))

            # 更新粒子狀態
            improved = trial_scores < self.pbest_scores
            self.particles[improved] = trial_particles[improved]
            self.pbest[improved] = trial_particles[improved]
            self.pbest_scores[improved] = trial_scores[improved]

            current_gbest_idx = np.argmin(self.pbest_scores)
            if self.pbest_scores[current_gbest_idx] < self.gbest_score:
                self.gbest_score = self.pbest_scores[current_gbest_idx]
                self.gbest = self.particles[current_gbest_idx].copy()

            convergence_curve.append(self.gbest_score)
    
        return self.gbest, self.gbest_score, convergence_curve, self.particles

class PSOCONTROL:
    __name__ = "PSO"
    def __init__(self,MAX_ITER, NUM_PARTICLES,  FUNCTION):
        self.MAX_ITER = MAX_ITER
        self.NUM_PARTICLES = NUM_PARTICLES
        self.UB = FUNCTION.ub
        self.LB = FUNCTION.lb
        self.DIM= FUNCTION.dim
        self.f = FUNCTION.func
        self.f_type = FUNCTION.f_type

    def start(self, init_population=None):
        pso = PSO(obj_function=self.f, dim=self.DIM, lb=self.LB, ub=self.UB, 
                  num_par=self.NUM_PARTICLES, max_iter=self.MAX_ITER, f_type=self.f_type,
                  init_population=init_population)
        best_position, best_value, curve, particles = pso.optimize()

        if self.f_type == "d":
            return (particles, np.array(curve))
        else:
            return (particles, np.log10(curve))

if __name__ == '__main__':
    pass