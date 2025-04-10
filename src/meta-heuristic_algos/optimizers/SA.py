import numpy as np
import matplotlib.pyplot as plt

from DataSet import DataSet

class SA:
    def __init__(self, obj_function, dim, lb, ub, max_iter, f_type, init_temp=1000, cooling_rate=0.95):
        self.obj_function = obj_function
        self.dim = dim
        self.lb = np.array(lb)
        self.ub = np.array(ub)
        self.max_iter = max_iter    
        self.temp = init_temp    
        self.cooling_rate = cooling_rate 
        self.f_type = f_type

        if self.f_type == "d":
            self.ub = np.append(self.ub, DataSet.NN_K)
            self.lb = np.append(self.lb, 1)
            self.dim += 1

        # initialization
        self.current = np.random.uniform(self.lb, self.ub, self.dim)
        self.current_fitness = self.obj_function(self.current)
        self.best = self.current.copy()
        self.best_fitness = self.current_fitness
    
    def neighbor(self, current_solution):
        # To generate neighbor solution
        neighbor = current_solution.copy()
        for i in range(self.dim):
            # 隨機決定用哪種擾動，這邊 80% 機率用小步長，20% 機率用大步長
            if np.random.rand() < 0.8:
                # 小幅擾動，可進一步乘上 (self.temp/self.init_temp) 當作動態調整
                step = np.random.normal(0, 0.1 * (self.temp/self.temp))
            else:
                # 大幅擾動，這裡直接用較大的標準差，可根據需求調整
                step = np.random.normal(0, 1.0)
            neighbor[i] += step
        neighbor = np.clip(neighbor, self.lb, self.ub)
        return neighbor

    def optimize(self):
        convergence_curve = []
        convergence_curve.append(self.best_fitness)

        for i in range(self.max_iter):
            new_solution = self.neighbor(self.current)
            new_fitness = self.obj_function(new_solution)

            delta = new_fitness - self.current_fitness
            if delta < 0:
                self.current = new_solution.copy()
                self.current_fitness = new_fitness
            else:
                # accept worse solution in probability
                if np.random.rand() < np.exp(-delta/self.temp):
                    self.current = new_solution.copy()
                    self.current_fitness = new_fitness

            if self.current_fitness < self.best_fitness:
                self.best_fitness = self.current_fitness
                self.best = self.current.copy()

            convergence_curve.append(self.best_fitness)
            self.temp *= self.cooling_rate
        return self.best, self.best_fitness, convergence_curve, self.current

class SACONTROL:
    __name__ = "SA"
    def __init__(self, MAX_ITER, Empty, FUNCTION, INIT_TEMP=1000, COOLING_RATE=0.95):
        self.MAX_ITER = MAX_ITER
        self.INIT_TEMP = INIT_TEMP
        self.COOLING_RATE = COOLING_RATE
        self.UB = FUNCTION.ub
        self.LB = FUNCTION.lb
        self.DIM = FUNCTION.dim
        self.f = FUNCTION.func
        self.f_type = FUNCTION.f_type

    def Start(self):
        sa = SA(obj_function=self.f, dim=self.DIM, lb=self.LB, ub=self.UB,
                max_iter=self.MAX_ITER, init_temp=self.INIT_TEMP, cooling_rate=self.COOLING_RATE,
                f_type=self.f_type)
        best_position, best_value, curve, final_solution = sa.optimize()

        if self.f_type == "d":
            return (final_solution, np.array(curve))
        else:
            return (final_solution, np.log10(curve))

if __name__ == '__main__':
    funcs_by_year = DataSet.funcs_years

    MAX_ITER = 500
    INIT_TEMP = 1000     
    COOLING_RATE = 0.95

    DIM = 10

    for year in funcs_by_year['CEC']:
        for func_name in funcs_by_year['CEC'][year]:
            function = DataSet().get_function(year, func_name, DIM)
            UB = function.ub
            LB = function.lb
            f = function.func

            sa = SA(obj_function=f, dim=DIM, lb=LB, ub=UB, max_iter=MAX_ITER,
                    init_temp=INIT_TEMP, cooling_rate=COOLING_RATE, f_type=function.f_type)
            best_position, best_value, curve, final_solution = sa.optimize()

            print(f"[CEC {year}-{func_name}] Best solution found:", best_position)
            print(f"[CEC {year}-{func_name}] Best fitness:", best_value)

            plt.plot(np.log10(curve))
            plt.xlabel("Generations")
            plt.ylabel("Fitness Value (Log10)")
            plt.title(f"SA Convergence {year}-{func_name}-{DIM}D")
            plt.show()
