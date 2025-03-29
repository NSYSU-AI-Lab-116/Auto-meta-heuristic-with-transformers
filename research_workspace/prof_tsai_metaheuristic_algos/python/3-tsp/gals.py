#!/usr/bin/env python
import numpy as np; import time; import sys; import os; import math
from lib import *

class gals:
    def __init__(self, num_runs = 3, num_evals = 120000, num_patterns_sol = 51, filename_ini = "", filename_ins = "eil51.tsp", pop_size = 100, crossover_rate = 0.4, mutation_rate = 0.1, num_players = 3, num_ls = 100, ls_flag = 0):
        self.num_runs = num_runs
        self.num_evals = num_evals
        self.num_patterns_sol = num_patterns_sol
        self.filename_ini = filename_ini
        self.filename_ins = filename_ins
        self.pop_size = pop_size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.num_players = num_players
        self.num_ls = num_ls
        self.ls_flag = ls_flag
        self.seed = int(time.time())
        np.random.seed(self.seed)

    def run(self):
        self.avg_obj_val = 0.0
        self.avg_obj_val_eval = np.zeros(self.num_evals)
        for r in range(self.num_runs):
            self.eval_count = 0
            self.best_so_far = sys.float_info.max
            curr_pop, curr_obj_vals = self.init()
            while self.eval_count < self.num_evals:
                # 1. evaluation
                curr_obj_vals = self.evaluate(curr_pop, self.dist)
                self.update_best_sol(curr_pop, curr_obj_vals)
                if 0:
                    for i in range(self.pop_size):
                        if self.best_so_far > curr_obj_vals[i]:
                            self.best_so_far = curr_obj_vals[i]
                        if self.eval_count < self.num_evals:
                            self.avg_obj_val_eval[self.eval_count] += self.best_so_far
                            self.eval_count += 1
                # 2. determination
                curr_pop = self.tournament_select(curr_pop, curr_obj_vals, self.num_players)
                # 3. transition
                curr_pop = self.crossover_ox(curr_pop, self.crossover_rate)
                curr_pop = self.mutate(curr_pop, self.mutation_rate)
                if self.ls_flag == 0:
                    curr_pop = self.two_opt(curr_pop, self.dist, self.num_ls)
                else:
                    curr_obj_vals = self.evaluate(curr_pop, self.dist)
                    n = 0
                    v = curr_obj_vals[0]
                    for i in range(1, self.pop_size):
                        if curr_obj_vals[i] < v:
                            n = i
                            v = curr_obj_vals[i]
                    curr_pop[n] = self.two_opt_sol(curr_pop[n], self.dist, self.num_ls)
                self.update_best_sol(curr_pop, curr_obj_vals)
            self.avg_obj_val += self.best_so_far
        # 4. output
        self.avg_obj_val /= self.num_runs
        self.avg_obj_val_eval /= self.num_runs
        for i in range(self.num_evals):
            print("%.3f" % self.avg_obj_val_eval[i])
        self.show_optimum()
        return curr_pop

    def init(self):
        # 1. initialization
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
            curr_pop = np.array([np.arange(self.num_patterns_sol) for i in range(self.pop_size)])
            for i in range(self.pop_size):
                np.random.shuffle(curr_pop[i])
        # 5. construct the distance matrix
        self.dist = np.zeros((self.num_patterns_sol, self.num_patterns_sol))
        for i in range(self.num_patterns_sol):
            for j in range(self.num_patterns_sol):
                self.dist[i][j] = math.dist(self.ins_tsp[i], self.ins_tsp[j])
        return curr_pop, np.zeros(self.pop_size)

    def evaluate(self, curr_pop, dist):
        tour_dist = np.zeros(self.pop_size)
        for p in range(self.pop_size):
            tour_dist[p] = self.evaluate_sol(curr_pop[p], dist)
        return tour_dist

    def evaluate_sol(self, curr_sol, dist):
        tour_dist = 0.0
        for i in range(self.num_patterns_sol):
            r = curr_sol[i]
            s = curr_sol[(i+1) % self.num_patterns_sol]
            tour_dist += self.dist[r][s]
        if self.best_so_far > tour_dist:
            self.best_so_far = tour_dist
        if self.eval_count < self.num_evals:
            self.avg_obj_val_eval[self.eval_count] += self.best_so_far
            self.eval_count += 1
        return tour_dist

    def update_best_sol(self, curr_pop, curr_obj_vals):
        for i in range(self.pop_size):
            if curr_obj_vals[i] < self.best_obj_val:
                self.best_obj_val = curr_obj_vals[i]
                self.best_sol = curr_pop[i]

    def tournament_select(self, curr_pop, curr_obj_vals, num_players):
        tmp_pop = np.zeros((self.pop_size, self.num_patterns_sol), dtype=int)
        for i in range(self.pop_size):
            k = np.random.randint(self.pop_size)
            f = curr_obj_vals[k]
            for j in range(1, num_players):
                n = np.random.randint(self.pop_size)
                if curr_obj_vals[n] < f:
                    k = n
                    f = curr_obj_vals[k]
            tmp_pop[i] = curr_pop[k]
        return tmp_pop

    def crossover_ox(self, curr_pop, cr):
        tmp_pop = curr_pop.copy()
        mid = self.pop_size // 2
        ssz = self.num_patterns_sol
        for i in range(mid):
            f = np.random.rand()
            if f <= cr:
                # 1. create the mapping sections
                xp1 = np.random.randint(ssz + 1)
                xp2 = np.random.randint(ssz + 1)
                if xp1 > xp2:
                    xp1, xp2 = xp2, xp1
                # 2. indices to the two parents and offspring
                p = [ i, i+mid ]
                # 3. the main process of ox
                for k in range(2):
                    c1 = p[k]
                    c2 = p[1-k]
                    # 4. mask the genes between xp1 and xp2
                    s1 = curr_pop[c1]
                    s2 = curr_pop[c2]
                    msk1 = np.zeros(ssz, dtype=bool)
                    for j in range(xp1, xp2):
                        msk1[s1[j]] = True
                    msk2 = np.zeros(ssz, dtype=bool)
                    for j in range(0, ssz):
                        msk2[j] = msk1[s2[j]]
                    # 5. replace the genes that are not masked
                    j = xp2 % ssz
                    for z in range(ssz):
                        if not msk2[z]:
                            tmp_pop[c1][j] = s2[z]
                            j = (j+1) % ssz
        return tmp_pop

    def mutate(self, curr_pop, mr):
        tmp_pop = curr_pop
        ssz = self.num_patterns_sol
        for i in range(self.pop_size):
            f = np.random.rand()
            if f <= mr:
                m1 = np.random.randint(ssz)     # mutation point
                m2 = np.random.randint(ssz)     # mutation point
                tmp_pop[i][m1], tmp_pop[i][m2] = tmp_pop[i][m2], tmp_pop[i][m1]
        return tmp_pop

    def two_opt(self, curr_pop, dist, num_ls):
        tmp_pop = np.zeros((self.pop_size, self.num_patterns_sol), dtype=int)
        for i in range(self.pop_size):
            tmp_pop[i] = self.two_opt_sol(curr_pop[i], dist, num_ls)
        return tmp_pop

    def two_opt_sol(self, curr_sol, dist, num_ls):
        r_start = np.random.randint(self.pop_size)
        ls_count = 0
        tmp_sol = curr_sol
        tmp_sol_dist = self.evaluate_sol(tmp_sol, dist)
        for i in range(r_start, self.num_patterns_sol - 1):
            for k in range(i+1, self.num_patterns_sol):
                tmp_sol_2opt = tmp_sol.copy()
                e = k
                for b in range(i, k+1):
                    tmp_sol_2opt[b] = tmp_sol[e]
                    e -= 1
                tmp_sol_2opt_dist = self.evaluate_sol(tmp_sol_2opt, dist)
                if tmp_sol_dist > tmp_sol_2opt_dist:
                    tmp_sol = tmp_sol_2opt
                    tmp_sol_dist = tmp_sol_2opt_dist
                ls_count += 1
                if ls_count == num_ls:
                    return tmp_sol
        return tmp_sol

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
        print("# population size: %s" % self.pop_size)
        print("# crossover rate: %s" % self.crossover_rate)
        print("# mutation rate: %s" % self.mutation_rate)
        print("# number of players: %s" % self.num_players)
        print("# number of local searches per evaluation: %s" % self.num_ls)
        print("# fine-tune? 0:population; 1:solution: %s" % self.ls_flag)
        print("# seed: %s" % self.seed)

def usage():
    lib.usage("<filename_ins> <pop_size> <cr> <mr> <#players> <#ls_per_eval> <ls sol?>")

if __name__ == "__main__":
    if ac() == 2 and ss(1) == "-h": usage()
    elif ac() == 1: search = gals()
    elif ac() == 12: search = gals(si(1), si(2), si(3), ss(4), ss(5), si(6), sf(7), sf(8), si(9), si(10), si(11))
    else: usage()
    lib.run(search, None)
