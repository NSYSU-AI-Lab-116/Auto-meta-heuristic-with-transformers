import numpy as np
import matplotlib as plt

from src.meta_heuristic_algos.Config import Configs
DataSet = Configs.DataSet

class GA:
    def __init__(self, obj_function, dim, lb, ub, pop_size, max_iter, f_type, mutation_rate=0.01, init_population=None):
        self.obj_function = obj_function
        self.dim = dim
        self.lb = np.array(lb)
        self.ub = np.array(ub)
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.f_type = f_type
        self.mutation_rate = mutation_rate

        if self.f_type == "d":
            self.ub = np.append(self.ub, DataSet.NN_K)
            self.lb = np.append(self.lb, 1)
            self.dim += 1

        if init_population is None:
            self.population = np.random.uniform(self.lb, self.ub, (self.pop_size, self.dim))
        else:
            self.population = init_population

        self.fitness = np.array([self.obj_function(idx) for idx in self.population])
        best_idx = np.argmin(self.fitness)
        self.gbest = self.population[best_idx].copy()
        self.gbest_score = self.fitness[best_idx]

    def selection(self, selection_size=3):
        indices = np.random.choice(self.pop_size, selection_size, replace=False)
        best = indices[0]
        for idx in indices:
            if self.fitness[idx] < self.fitness[best]:
                best = idx
        return self.population[best].copy()
    
    def crossover(self, mother, father):
        # 50% for selecting parent gene
        mask = np.random.rand(self.dim) < 0.5
        child = np.where(mask, mother, father)
        return child

    def mutate(self, child):
        for i in range(self.dim):
            if np.random.rand() < self.mutation_rate:
                child[i] += np.random.normal(0, 0.1)
    
        child = np.clip(child, self.lb, self.ub)
        return child

    def optimize(self):
        convergence_curve = []
        convergence_curve.append(self.gbest_score) # first generation

        for i in range(self.max_iter):
            new_population = []
            new_fitness = []
            # elite retention
            new_population.append(self.gbest.copy())
            new_fitness.append(self.gbest_score)

            while(len(new_population) != self.pop_size):
                mother = self.selection()
                father = self.selection()
                child = self.crossover(mother=mother,father=father)
                child = self.mutate(child)
                child_fitness = self.obj_function(child)

                new_population.append(child)
                new_fitness.append(child_fitness)

            self.population = np.array(new_population)
            self.fitness = np.array(new_fitness)

            # update
            gen_best_idx = np.argmin(self.fitness)
            if self.fitness[gen_best_idx] < self.gbest_score:
                self.gbest_score = self.fitness[gen_best_idx]
                self.gbest = self.population[gen_best_idx].copy()

            convergence_curve.append(self.gbest_score)
        return self.gbest, self.gbest_score, convergence_curve, self.population

class GACONTROL:
    __name__ = "GA"
    def __init__(self, MAX_ITER, POP_SIZE, FUNCTION, mutation_rate=0.01):
        self.MAX_ITER = MAX_ITER
        self.POP_SIZE = POP_SIZE
        self.UB = FUNCTION.ub
        self.LB = FUNCTION.lb
        self.DIM = FUNCTION.dim
        self.f = FUNCTION.func
        self.f_type = FUNCTION.f_type
        self.mutation_rate = mutation_rate
    
    def start(self, init_population=None):
        ga = GA(obj_function=self.f, dim=self.DIM, lb=self.LB, ub=self.UB, 
                pop_size=self.POP_SIZE, max_iter=self.MAX_ITER, f_type=self.f_type,
                mutation_rate=self.mutation_rate, init_population=init_population)
        best_position, best_value, curve, population = ga.optimize()
        
        if self.f_type == "d":
            return (population, np.array(curve))
        else:
            return (population, curve)

if __name__ == '__main__':
    """ funcs_by_year = DataSet.funcs_years

    MAX_ITER = 500
    POP_SIZE = 30
    DIM = 10

    for year in funcs_by_year['CEC']:
        for func_name in funcs_by_year['CEC'][year]:
            function = DataSet().get_function(year, func_name, DIM)
            UB = function.ub
            LB = function.lb
            f = function.func

            ga = GA(obj_function=f, dim=DIM, lb=LB, ub=UB, pop_size=POP_SIZE,
                    max_iter=MAX_ITER, f_type=function.f_type)
            best_position, best_value, curve, population = ga.optimize()

            print(f"[CEC {year}-{func_name}] Best solution found:", best_position)
            print(f"[CEC {year}-{func_name}] Best fitness:", best_value)

            plt.plot(np.log10(curve))
            plt.xlabel("Generations")
            plt.ylabel("Fitness Value (Log10)")
            plt.title(f"GA Convergence {year}-{func_name}-{DIM}D")
            plt.show() """