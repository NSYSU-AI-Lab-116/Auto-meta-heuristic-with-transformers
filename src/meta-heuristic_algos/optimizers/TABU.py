import numpy as np
import matplotlib.pyplot as plt

from DataSet import DataSet

class TS:
    def __init__(self, obj_function, dim, lb, ub, max_iter, f_type, tabu_list_size=5, num_neighbors=10, tolerance=1e-4):
        self.obj_function = obj_function
        self.dim = dim
        self.lb = np.array(lb)
        self.ub = np.array(ub)
        self.max_iter = max_iter
        self.f_type = f_type
        self.tabu_list_size = tabu_list_size   
        self.num_neighbors = num_neighbors     
        self.tolerance = tolerance             

        if self.f_type == "d":
            self.ub = np.append(self.ub, DataSet.NN_K)
            self.lb = np.append(self.lb, 1)
            self.dim += 1

        # initialization
        self.current = np.random.uniform(self.lb, self.ub, self.dim)
        self.current_fitness = self.obj_function(self.current)
        self.best = self.current.copy()
        self.best_fitness = self.current_fitness
        self.tabu_list = []

    def is_tabu(self, solution):
        # check if any similar solution in Tabu list
        for tabu_sol in self.tabu_list:
            if np.linalg.norm(solution - tabu_sol) < self.tolerance:
                return True
        return False

    def generate_neighbors(self, current_solution):
        neighbors = []
        for _ in range(self.num_neighbors):
            neighbor = current_solution.copy()
            for j in range(self.dim):
                # generate neighbor solution by guassian 
                neighbor[j] += np.random.normal(0, 0.1)
            neighbor = np.clip(neighbor, self.lb, self.ub)
            neighbors.append(neighbor)
        return neighbors
    
    def optimize(self):
        convergence_curve = []
        convergence_curve.append(self.best_fitness)

        for i in range(self.max_iter):
            # generate candidate neighbor solution
            neighbors = self.generate_neighbors(self.current)
            best_candidate = None
            best_candidate_fitness = np.inf

            # Select one with NOT Tabu and best fitness
            for candidate in neighbors:
                if not self.is_tabu(candidate):
                    fitness_candidate = self.obj_function(candidate)
                    if fitness_candidate < best_candidate_fitness:
                        best_candidate_fitness = fitness_candidate
                        best_candidate = candidate.copy()
            
            # All Tabu -> Select the best
            if best_candidate is None:
                for candidate in neighbors:
                    fitness_candidate = self.obj_function(candidate)
                    if fitness_candidate < best_candidate_fitness:
                        best_candidate_fitness = fitness_candidate
                        best_candidate = candidate.copy()
            
            # Update Tabu list
            self.tabu_list.append(self.current.copy())
            if len(self.tabu_list) > self.tabu_list_size:
                self.tabu_list.pop(0)
            
            self.current = best_candidate.copy()
            self.current_fitness = best_candidate_fitness

            # update global optima
            if self.current_fitness < self.best_fitness:
                self.best_fitness = self.current_fitness
                self.best = self.current.copy()

            convergence_curve.append(self.best_fitness)

        return self.best, self.best_fitness, convergence_curve, self.current

class TSCONTROL:
    __name__ = "TS"
    def __init__(self, MAX_ITER, EMPTY,FUNCTION, TABU_SIZE=5, NUM_NEIGHBORS=10, TOLERANCE=1e-4):
        self.MAX_ITER = MAX_ITER
        self.TABU_SIZE = TABU_SIZE
        self.NUM_NEIGHBORS = NUM_NEIGHBORS
        self.TOLERANCE = TOLERANCE
        self.UB = FUNCTION.ub
        self.LB = FUNCTION.lb
        self.DIM = FUNCTION.dim
        self.f = FUNCTION.func
        self.f_type = FUNCTION.f_type

    def Start(self):
        ts = TS(obj_function=self.f, dim=self.DIM, lb=self.LB, ub=self.UB,
                max_iter=self.MAX_ITER, f_type=self.f_type,
                tabu_list_size=self.TABU_SIZE, num_neighbors=self.NUM_NEIGHBORS, tolerance=self.TOLERANCE)
        best_position, best_value, curve, final_solution = ts.optimize()
        if self.f_type == "d":
            return (final_solution, np.array(curve))
        else:
            return (final_solution, np.log10(curve))

if __name__ == '__main__':
    funcs_by_year = DataSet.funcs_years

    MAX_ITER = 500
    TABU_SIZE = 5
    NUM_NEIGHBORS = 10
    TOLERANCE = 1e-4
    DIM = 10

    for year in funcs_by_year['CEC']:
        for func_name in funcs_by_year['CEC'][year]:
            function = DataSet.get_function(year, func_name, DIM)
            UB = function.ub
            LB = function.lb
            f = function.func

            ts = TS(obj_function=f, dim=DIM, lb=LB, ub=UB, max_iter=MAX_ITER,
                    f_type=function.f_type, tabu_list_size=TABU_SIZE, num_neighbors=NUM_NEIGHBORS, tolerance=TOLERANCE)
            best_position, best_value, curve, final_solution = ts.optimize()

            print(f"[CEC {year}-{func_name}] Best solution found:", best_position)
            print(f"[CEC {year}-{func_name}] Best fitness:", best_value)

            plt.plot(np.log10(curve))
            plt.xlabel("Iterations")
            plt.ylabel("Fitness Value (Log10)")
            plt.title(f"TS Convergence {year}-{func_name}-{DIM}D")
            plt.show() 