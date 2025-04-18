import os
import numpy as np
from joblib import Parallel, delayed
from src.meta_heuristic_algos.Config import Configs

DataSet = Configs.DataSet
JOBS_INNER = max(1, Configs.executer_num)  # 依外層 CPU 使用量手動調整


def safe_eval(fn, ind, idx):
    # ensure different seed
    np.random.seed(os.getpid() & 0xFFFF)
    return fn(ind, idx)


def parallel_eval(fn, pop):
    return np.array(
        Parallel(n_jobs=JOBS_INNER, backend="loky", verbose=0)(
            delayed(safe_eval)(fn, ind, i) for i, ind in enumerate(pop)
        )
    )


class DE:
    """Differential Evolution algorithm for optimization (with joblib inner‑population parallel)."""

    def __init__(
        self,
        obj_function,
        dim,
        lb,
        ub,
        num_par,
        max_iter,
        f_type,
        factor=0.5,
        cross_rate=0.9,
        init_population=None,
    ):
        self.obj_function = obj_function
        self.dim = dim
        self.lb = np.array(lb)
        self.ub = np.array(ub)
        self.num_par = num_par
        self.max_iter = int(max_iter)
        self.f_type = f_type
        self.factor = factor  # scaling factor
        self.cross_rate = cross_rate  # cross rate

        if self.f_type == "d":
            self.ub = np.append(self.ub, DataSet.NN_K)
            self.lb = np.append(self.lb, 1)
            self.dim += 1

        if init_population is None:
            self.population = np.random.uniform(self.lb, self.ub, (self.num_par, self.dim))
        else:
            self.population = init_population

        # initial fitness(parallel)
        self.fitness = parallel_eval(self.obj_function, self.population)
        best_idx = int(np.argmin(self.fitness))
        self.gbest = self.population[best_idx].copy()
        self.gbest_score = float(self.fitness[best_idx])


    def optimize(self):
        curve = [self.gbest_score]
        rng = np.random.default_rng()

        for _ in range(self.max_iter):
            trial_pop = np.zeros_like(self.population)
            for i in range(self.num_par):
                trial_pop[i] = self.core_logic(i, rng)

            # evaluate(parallel)
            trial_fitness = parallel_eval(self.obj_function, trial_pop)

            replace = trial_fitness < self.fitness
            self.population[replace] = trial_pop[replace]
            self.fitness[replace] = trial_fitness[replace]

            best_idx = int(np.argmin(self.fitness))
            self.gbest_score = float(self.fitness[best_idx])
            self.gbest = self.population[best_idx].copy()
            curve.append(self.gbest_score)

        return self.gbest, self.gbest_score, curve, self.population

    def core_logic(self, i, rng):
        idxs = list(range(self.num_par))
        idxs.remove(i)
        a, b, c = self.population[np.random.choice(idxs, 3, replace=False)]
        donor = a + self.factor * (b - c)

        trial = donor.copy()
        j_rand = rng.integers(self.dim)
        for j in range(self.dim):
            if j != j_rand and rng.random() >= self.cross_rate:
                trial[j] = self.population[i, j]

        if self.f_type == "d":
            trial[:-1] = np.clip(trial[:-1], DataSet.param_LB, DataSet.param_UB)
            trial[-1] = np.clip(trial[-1], 1, DataSet.NN_K)
        else:
            trial = np.clip(trial, self.lb, self.ub)

        trial_fitness = self.obj_function(trial, i)
        if trial_fitness < self.fitness[i]:
            self.population[i] = trial
            self.fitness[i] = trial_fitness


class DECONTROL:
    """Wrapper for Differential Evolution algorithm."""

    __name__ = "DE"

    def __init__(
        self,
        max_iter,
        num_individual,
        function,
        factor=0.5,
        cross_rate=0.9,
    ):
        self.max_iter = max_iter
        self.num_individual = num_individual
        self.ub = function.ub
        self.lb = function.lb
        self.dim = function.dim
        self.f = function.func
        self.f_type = function.f_type
        self.factor = factor
        self.cross_rate = cross_rate

    def start(self, init_population=None):
        de = DE(
            obj_function=self.f,
            dim=self.dim,
            lb=self.lb,
            ub=self.ub,
            num_par=self.num_individual,
            max_iter=self.max_iter,
            f_type=self.f_type,
            factor=self.factor,
            cross_rate=self.cross_rate,
            init_population=init_population,
        )
        best_position, best_value, curve, population = de.optimize()

        if self.f_type == "d":
            return (population, np.array(curve))
        else:
            return (population, np.log10(curve))


if __name__ == "__main__":
    pass