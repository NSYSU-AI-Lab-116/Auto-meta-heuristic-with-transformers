import numpy as np
import math
import matplotlib.pyplot as plt

from src.python.Config import Configs
DataSet = Configs.DataSet

def logistics_chaotic_map(dim, iteration=10, value=1):
    x0 = np.zeros(dim) + 0.7
    for i in range(iteration):
        x0 = 4 * x0 * (1 - x0)
    return x0

class ChOA:
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
            self.chimps = np.random.uniform(self.lb, self.ub, (self.num_pop, self.dim))
        else:
            self.chimps = init_population

        self.attacker = self.chimps[0].copy()
        self.chaser = self.chimps[1].copy()
        self.barrier = self.chimps[2].copy()
        self.driven = self.chimps[3].copy()
        self.scores = np.full(self.num_pop, np.inf)

    def logistics_chaotic_map(self, dim, iteration=10, value=1):
        x0 = np.zeros(dim) + 0.7
        for i in range(iteration):
            x0 = 4 * x0 * (1 - x0)
        return x0

    def optimize(self):
        convergence_curve = []
        for t in range(self.max_iter):
            f = 2.5 - (t * (2.5 / self.max_iter))

            for i in range(self.num_pop):
                self.scores[i] = self.obj_function(self.chimps[i])

            sorted_indices = np.argsort(self.scores)
            self.attacker = self.chimps[sorted_indices[0]].copy()
            self.chaser = self.chimps[sorted_indices[1]].copy()
            self.barrier = self.chimps[sorted_indices[2]].copy()
            self.driven = self.chimps[sorted_indices[3]].copy()

            for i in range(self.num_pop):
                m = self.logistics_chaotic_map(1)

                r1, r2 = np.random.rand(), np.random.rand()
                A1 = 2 * f * r1 - f
                C1 = 2 * r2
                D_attacker = abs(C1 * self.attacker - m * self.chimps[i])
                X1 = self.attacker - A1 * D_attacker

                r1, r2 = np.random.rand(), np.random.rand()
                A2 = 2 * f * r1 - f
                C2 = 2 * r2
                D_chaser = abs(C2 * self.chaser - m * self.chimps[i])
                X2 = self.chaser - A2 * D_chaser

                r1, r2 = np.random.rand(), np.random.rand()
                A3 = 2 * f * r1 - f
                C3 = 2 * r2
                D_barrier = abs(C3 * self.barrier - m * self.chimps[i])
                X3 = self.barrier - A3 * D_barrier

                r1, r2 = np.random.rand(), np.random.rand()
                A4 = 2 * f * r1 - f
                C4 = 2 * r2
                D_driven = abs(C4 * self.driven - m * self.chimps[i])
                X4 = self.driven - A4 * D_driven

                self.chimps[i] = (X1 + X2 + X3 + X4) / 4

                if self.f_type == "d":
                    self.chimps[i][-1] = np.clip(self.chimps[i][-1], 1, DataSet.NN_K)
                    self.chimps[i][:-1] = np.clip(self.chimps[i][:-1], DataSet.param_LB, DataSet.param_UB)
                else:
                    self.chimps[i] = np.clip(self.chimps[i], self.lb, self.ub)

            self.chimps[-1] = self.attacker.copy()
            convergence_curve.append(self.scores[sorted_indices[0]])

        return self.attacker, self.scores[sorted_indices[0]], convergence_curve, self.chimps


class ChOACONTROL:
    __name__ = "ChOA"
    def __init__(self, MAX_ITER, NUM_CHIMPS, FUNCTION):
        self.MAX_ITER = MAX_ITER
        self.NUM_CHIMPS = NUM_CHIMPS
        self.UB = FUNCTION.ub
        self.LB = FUNCTION.lb
        self.DIM = FUNCTION.dim
        self.f = FUNCTION.func
        self.f_type = FUNCTION.f_type

    def start(self, init_population=None):
        choa = ChOA(obj_function=self.f, dim=self.DIM, lb=self.LB, ub=self.UB, 
                    num_pop=self.NUM_CHIMPS, max_iter=self.MAX_ITER, f_type=self.f_type, init_population=init_population)
        best_position, best_value, curve, chimps = choa.optimize()

        if self.f_type == "d":
            return (chimps, np.array(np.abs(curve)))
        else:
            return (chimps, curve)

if __name__ == '__main__':
    pass
