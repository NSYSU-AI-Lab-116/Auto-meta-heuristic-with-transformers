import numpy as np
import matplotlib.pyplot as plt

from DataSet import DataSet

class DE:
    def __init__(self, obj_function, dim, lb, ub, num_par, max_iter, f_type, F=0.5, CR=0.9, init_population=None):
        self.obj_function = obj_function
        self.dim = dim
        self.lb = np.array(lb)
        self.ub = np.array(ub)
        self.num_par = num_par
        self.max_iter = max_iter
        self.f_type = f_type
        self.F = F      # scaling factor
        self.CR = CR    # cross rate

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
        convergence_curve = []

        # initializationn
        for i in range(self.num_par):
            self.fitness[i] = self.obj_function(self.population[i])
            if self.fitness[i] < self.gbest_score:
                self.gbest_score = self.fitness[i]
                self.gbest = self.population[i].copy()
        
        # iteration
        for t in range(self.max_iter):
            for i in range(self.num_par):
                # randomly select 
                idxs = list(range(self.num_par))
                idxs.remove(i)
                a, b, c = self.population[np.random.choice(idxs, 3, replace=False)]

                donor = a + self.F*(b - c)

                # compute trial solution (by crossing)
                trial = np.empty(self.dim)
                j_rand = np.random.randint(self.dim)
                for j in range(self.dim):
                    if j == j_rand or np.random.rand() < self.CR:
                        trial[j] = donor[j]
                    else:
                        trial[j] = self.population[i][j]

                # border handle
                if self.f_type == "d":
                    trial[:-1] = np.clip(trial[:-1], DataSet.param_LB, DataSet.param_UB)
                    trial[-1] = np.clip(trial[-1], 1, DataSet.NN_K)
                else:
                    trial = np.clip(trial, self.lb, self.ub)
                
                trial_fitness = self.obj_function(trial)
                # verify trial solution
                if trial_fitness < self.fitness[i]:
                    self.population[i] = trial
                    self.fitness[i] = trial_fitness
                    if trial_fitness < self.gbest_score:
                        self.gbest_score = trial_fitness
                        self.gbest = trial.copy()

            convergence_curve.append(self.gbest_score)
        return self.gbest, self.gbest_score, convergence_curve, self.population
    
class DECONTROL:
    __name__="DE"  
    def __init__(self, MAX_ITER, NUM_PARTICLES, FUNCTION, F = 0.5, CR = 0.9):
        self.MAX_ITER = MAX_ITER
        self.NUM_PARTICLES = NUM_PARTICLES
        self.UB = FUNCTION.ub
        self.LB = FUNCTION.lb
        self.DIM = FUNCTION.dim
        self.f = FUNCTION.func
        self.f_type = FUNCTION.f_type
        self.F = F
        self.CR = CR

    def Start(self, init_population=None):
        de = DE(obj_function=self.f, dim=self.DIM, lb=self.LB, ub=self.UB, 
                num_par=self.NUM_PARTICLES, max_iter=self.MAX_ITER, f_type=self.f_type, F=self.F, CR=self.CR, init_population=init_population)
        best_position, best_value, curve, population = de.optimize()

        if self.f_type == "d":
            return (population, np.array(curve))
        else:
            return (population, np.log10(curve))

if __name__ == '__main__':
    funcs_by_year = DataSet.funcs_years

    MAX_ITER = 500
    NUM_PARTICLES = 30
    DIM = 10

    for year in funcs_by_year['CEC']:
        for func_name in funcs_by_year['CEC'][year]:
            function = DataSet.get_function(year, func_name, DIM)
            UB = function.ub
            LB = function.lb
            f = function.func

            de = DE(obj_function=f, dim=DIM, lb=LB, ub=UB, num_par=NUM_PARTICLES, max_iter=MAX_ITER, f_type=function.f_type)
            best_position, best_value, curve, population = de.optimize()

            print(f"[CEC {year}-{func_name}] Best solution found:", best_position)
            print(f"[CEC {year}-{func_name}] Best fitness:", best_value)

            plt.plot(np.log10(curve))
            plt.xlabel("Iterations")
            plt.ylabel("Fitness Value (Log10)")
            plt.title(f"DE Convergence {year}-{func_name}-{DIM}D")
            plt.show()