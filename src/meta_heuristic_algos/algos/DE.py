"""Model for Differential Evolution (DE) algorithm."""
import numpy as np
from src.meta_heuristic_algos.Config import Configs
from concurrent.futures import ProcessPoolExecutor
DataSet = Configs.DataSet

class DE:
    """ Differential Evolution algorithm for optimization."""
    def __init__(self, obj_function, dim, lb, ub, num_par, max_iter,
                 f_type, factor=0.5, cross_rate=0.9, init_population=None):

        self.obj_function = obj_function
        self.dim = dim
        self.lb = np.array(lb)
        self.ub = np.array(ub)
        self.num_par = num_par
        self.max_iter = int(max_iter)
        self.f_type = f_type
        self.factor = factor      # scaling factor
        self.cross_rate = cross_rate    # cross rate

        if self.f_type == "d":
            self.ub = np.append(self.ub, DataSet.NN_K)
            self.lb = np.append(self.lb, 1)
            self.dim += 1

        if init_population is None:
            self.population = np.random.uniform(self.lb, self.ub, (self.num_par, self.dim))
        else:
            self.population = init_population

        self.fitness = np.array([np.inf] * self.num_par)
        self.gbest = None
        self.gbest_score = np.inf

    def optimize(self):
        """ Perform the optimization process. """
        convergence_curve = []

        # initializationn
        if self.f_type == "hyperheuristic":
            with ProcessPoolExecutor() as executor:
                futures = [executor.submit(self.obj_function, self.population[i], i) for i in range(self.num_par)]
                for i, future in enumerate(futures):
                    self.fitness[i] = future.result()
                    if self.fitness[i] < self.gbest_score:
                        self.gbest_score = self.fitness[i]
                        self.gbest = self.population[i].copy()
        else:
            for i in range(self.num_par):
                self.fitness[i] = self.obj_function(self.population[i],i)
                if self.fitness[i] < self.gbest_score:
                    self.gbest_score = self.fitness[i]
                    self.gbest = self.population[i].copy()

        # iteration
        for current_iter in range(self.max_iter):
            if self.f_type == "hyperheuristic":
                print(f"{Configs.Color.RED}Hyperheuristic iter:{current_iter}{Configs.Color.RESET}")
                with ProcessPoolExecutor() as executor:
                    futures = [executor.submit(self.core_logic,i) for i in range(self.num_par)]
                    for future in futures:
                        future.result()
            else:
                for i in range(self.num_par):
                    self.core_logic(i)

            convergence_curve.append(self.gbest_score)
        return self.gbest, self.gbest_score, convergence_curve, self.population   

    def core_logic(self,i):
        # randomly select
        idxs = list(range(self.num_par))
        idxs.remove(i)
        a, b, c = self.population[np.random.choice(idxs, 3, replace=False)]

        donor = a + self.factor*(b - c)

        # compute trial solution (by crossing)
        trial = np.empty(self.dim)
        j_rand = np.random.randint(self.dim)
        for j in range(self.dim):
            if j == j_rand or np.random.rand() < self.cross_rate:
                trial[j] = donor[j]
            else:
                trial[j] = self.population[i][j]

        # border handle
        if self.f_type == "d":
            trial[:-1] = np.clip(trial[:-1], DataSet.param_LB, DataSet.param_UB)
            trial[-1] = np.clip(trial[-1], 1, DataSet.NN_K)
        else:
            trial = np.clip(trial, self.lb, self.ub)

        trial_fitness = self.obj_function(trial,i)
        # verify trial solution
        if trial_fitness < self.fitness[i]:
            self.population[i] = trial
            self.fitness[i] = trial_fitness
            if trial_fitness < self.gbest_score:
                self.gbest_score = trial_fitness
                self.gbest = trial.copy()



class DECONTROL:
    """ Control class for Differential Evolution algorithm."""
    __name__="DE"
    def __init__(self, max_iter, num_individual, function, factor = 0.5, cross_rate = 0.9):
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
        """ Start the DE optimization process. """
        de = DE(obj_function=self.f, dim=self.dim, lb=self.lb, ub=self.ub,
                num_par=self.num_individual, max_iter=self.max_iter, f_type=self.f_type, factor=self.factor, cross_rate=self.cross_rate, init_population=init_population)
        best_position, best_value, curve, population = de.optimize()

        if self.f_type == "d":
            return (population, np.array(curve))
        else:
            return (population, np.log10(curve))

if __name__ == '__main__':
    pass
