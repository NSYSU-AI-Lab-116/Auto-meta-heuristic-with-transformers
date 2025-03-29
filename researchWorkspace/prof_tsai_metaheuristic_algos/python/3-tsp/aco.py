#!/usr/bin/env python
import numpy as np; import time; import sys; import os; import math
from lib import *

class aco:
    def __init__(self, num_runs = 3, num_evals = 25000, num_patterns_sol = 51, filename_ini = "", filename_ins = "eil51.tsp", pop_size = 20, alpha = 0.1, beta = 2.0, rho = 0.1, q0 = 0.9):
        self.num_runs = num_runs
        self.num_evals = num_evals
        self.num_patterns_sol = num_patterns_sol
        self.filename_ini = filename_ini
        self.filename_ins = filename_ins
        self.pop_size = pop_size
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.q0 = q0
        self.seed = int(time.time())
        np.random.seed(self.seed)

    def run(self):
        avg_obj_val = 0.0
        avg_obj_val_eval = np.zeros(self.num_evals)
        for r in range(self.num_runs):
            eval_count = 0
            best_so_far = sys.float_info.max
            # 0. initialization
            curr_pop, curr_obj_vals = self.init()
            while eval_count < self.num_evals:
                # 1. transition
                self.construct_solutions(curr_pop, self.dist, self.ph, self.beta, self.q0)
                # 2. evaluation
                curr_obj_vals = self.evaluate(curr_pop)
                for i in range(self.pop_size):
                    if best_so_far > curr_obj_vals[i]:
                        best_so_far = curr_obj_vals[i]
                    if eval_count < self.num_evals:
                        avg_obj_val_eval[eval_count] += best_so_far
                        eval_count += 1
                # 3. determination
                self.update_best_sol(curr_pop, curr_obj_vals)
                self.update_global_ph(self.ph, self.best_sol, self.best_obj_val)
            avg_obj_val += self.best_obj_val
        # 4. output
        avg_obj_val /= self.num_runs
        for i in range(self.num_evals):
            avg_obj_val_eval[i] /= self.num_runs
            print("%.3f" % avg_obj_val_eval[i])
        self.show_optimum()
        # return curr_pop
        return self.best_sol

    def init(self):
        # 1. initialization
        curr_obj_vals = np.zeros(self.pop_size)
        self.best_sol = np.zeros(self.num_patterns_sol, dtype=int)
        self.best_obj_val = sys.float_info.max
        # 2. input the TSP benchmark
        with open(self.filename_ins, "r") as f:
            self.ins_tsp = np.array(f.read().strip().split(), dtype=float).reshape(self.num_patterns_sol, 2)
        # 3. input the optimal solution
        with open(self.filename_ins + ".opt", "r") as f:
            self.opt_sol = np.array(f.read().strip().split(), dtype=int) - 1
        # 4. initial solutions
        if len(self.filename_ini) > 0:
            with open(self.filename_ini, "r") as f:
                curr_pop = np.array(f.read().strip().split(), dtype=int).reshape(self.pop_size, self.num_patterns_sol)
        else:
            curr_pop = np.array([np.arange(self.num_patterns_sol) for i in range(self.pop_size)]).reshape(self.pop_size, self.num_patterns_sol)
            for i in range(self.pop_size):
                np.random.shuffle(curr_pop[i])
        # 5. construct the distance matrix
        self.ph = np.zeros((self.num_patterns_sol, self.num_patterns_sol))
        self.dist = np.zeros((self.num_patterns_sol, self.num_patterns_sol))
        for i in range(self.num_patterns_sol):
            for j in range(self.num_patterns_sol):
                self.dist[i][j] = math.dist(self.ins_tsp[i], self.ins_tsp[j])
        # 6. create the pheromone table, by first constructing a solution using the nearest neighbor method
        n = np.random.randint(self.pop_size)
        cities = list(curr_pop[n])
        self.best_sol[0] = cities[0]
        cities.pop(0)
        Lnn = 0.0
        for i in range(1, self.num_patterns_sol):
            r = self.best_sol[i-1]
            min_s = cities[0]   # simply choose a city
            min_dist = sys.float_info.max
            for s in cities:
                if self.dist[r][s] < min_dist:
                    min_dist = self.dist[r][s]
                    min_s = s
            s = min_s
            self.best_sol[i] = s
            cities.remove(min_s)
            Lnn += self.dist[r][s]
        r = self.best_sol[self.num_patterns_sol-1]
        s = self.best_sol[0]
        Lnn += self.dist[r][s]
        self.tau0 = 1 / (self.num_patterns_sol * Lnn)
        for r in range(self.num_patterns_sol):
            for s in range(self.num_patterns_sol):
                self.ph[r][s] = 0.0 if r == s else self.tau0
        return curr_pop, curr_obj_vals

    def construct_solutions(self, curr_pop, dist, ph, beta, q0):
        # 1. tau eta
        tau_eta = np.zeros((self.num_patterns_sol, self.num_patterns_sol))
        for r in range(self.num_patterns_sol):
            for s in range(self.num_patterns_sol):
                tau_eta[r][s] = 0.0 if r == s else ph[r][s] * math.pow(1.0 / dist[r][s], beta)
        # 2. construct the solution: first, the first city of the tour
        tmp_pop = curr_pop.tolist()
        for j in range(self.pop_size):
            asol = tmp_pop[j]
            n = np.random.randint(self.num_patterns_sol)
            curr_pop[j][0] = asol[n]
            asol.remove(asol[n])
        # 3. then, the remaining cities of the tour
        for i in range(1, self.num_patterns_sol):
            # for each step
            for j in range(self.pop_size):
                # for each ant
                asol = tmp_pop[j]
                r = curr_pop[j][i-1]
                s = asol[0]
                x = 0
                q = np.random.rand()
                if q <= q0:
                    # 3.1. exploitation
                    max_tau_eta = tau_eta[r][s]
                    for k in range(len(asol)):
                        if tau_eta[r][asol[k]] > max_tau_eta:
                            s = asol[k]
                            x = k
                            max_tau_eta = tau_eta[r][s]
                else:
                    # 3.2. biased exploration
                    total = 0.0
                    for k in range(len(asol)):
                        total += tau_eta[r][asol[k]]
                    # 3.3. choose the next city based on the probability
                    f = total * np.random.rand()
                    for k in range(len(asol)):
                        f -= tau_eta[r][asol[k]]
                        if f <= 0:
                            s = asol[k]
                            x = k
                            break
                curr_pop[j][i] = s
                asol.remove(asol[x])
                # 4.1. update local pheromones, 0 to n-1
                self.update_local_ph(ph, r, s)
        # 4.2. update local pheromones, n-1 to 0
        for k in range(self.pop_size):
            # for each ant
            r = curr_pop[k][self.num_patterns_sol-1]
            s = curr_pop[k][0]
            self.update_local_ph(ph, r, s)

    def evaluate(self, curr_pop):
        tour_dist = np.zeros(self.pop_size)
        for k in range(self.pop_size):
            for i in range(self.num_patterns_sol):
                r = curr_pop[k][i]
                s = curr_pop[k][(i+1) % self.num_patterns_sol]
                tour_dist[k] += self.dist[r][s]
        return tour_dist

    def update_best_sol(self, curr_pop, curr_obj_vals):
        for i in range(self.pop_size):
            if curr_obj_vals[i] < self.best_obj_val:
                self.best_obj_val = curr_obj_vals[i].copy()
                self.best_sol = curr_pop[i].copy()

    def update_global_ph(self, ph, best_sol, best_obj_val):
        for i in range(self.num_patterns_sol):
            r = best_sol[i]
            s = best_sol[(i+1) % self.num_patterns_sol]
            ph[s][r] = ph[r][s] = (1 - self.alpha) * ph[r][s] + self.alpha * (1 / self.best_obj_val)

    def update_local_ph(self, ph, r, s):
        ph[s][r] = ph[r][s] = (1 - self.rho) * ph[r][s] + self.rho * self.tau0

    def show_optimum(self):
        opt_dist = 0.0
        for i in range(self.num_patterns_sol):
            r = self.opt_sol[i]
            s = self.opt_sol[(i+1) % self.num_patterns_sol]
            opt_dist += self.dist[r][s]
        lib.print_solution(self.best_sol, prefix = "# Current route: ")
        lib.printf("# Optimum distance: %.3f", opt_dist)
        lib.print_solution(self.opt_sol, prefix = "# Optimum route: ")

    def print_parameters(self, algname):
        print("# name of the search algorithm: '%s'" % algname)
        print("# number of runs: %s" % self.num_runs)
        print("# number of evaluations: %s" % self.num_evals)
        print("# number of patterns (subsolutions) each solution: %s" % self.num_patterns_sol)
        print("# filename of the initial seeds: '%s'" % self.filename_ini)
        print("# filename of the benchmark: '%s'" % self.filename_ins)
        print("# population size (i.e., number of ants): %s" % self.pop_size)
        print("# alpha: %s" % self.alpha)
        print("# beta: %s" % self.beta)
        print("# rho: %s" % self.rho)
        print("# Q: %s" % self.q0)
        print("# seed: %s" % self.seed)

def usage():
    lib.usage("<filename_ins> <pop_size> <alpha> <beta> <rho> <Q>")

if __name__ == "__main__":
    if ac() == 2 and ss(1) == "-h": usage()
    elif ac() == 1: search = aco()
    elif ac() == 11: search = aco(si(1), si(2), si(3), ss(4), ss(5), si(6), sf(7), sf(8), sf(9), sf(10))
    else: usage()
    lib.run(search, None)
