#!/usr/bin/env python
import numpy as np; import time; import sys; import os; import math
from lib import *

class ga:
    def __init__(self, num_runs = 3, num_evals = 120000, num_patterns_sol = 1002, filename_ini = "", filename_ins = "pr1002.tsp", pop_size = 120, crossover_rate = 0.4, mutation_rate = 0.1, num_players = 3):
        self.num_runs = num_runs
        self.num_evals = num_evals
        self.num_patterns_sol = num_patterns_sol
        self.filename_ini = filename_ini
        self.filename_ins = filename_ins
        self.pop_size = pop_size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.num_players = num_players
        self.seed = int(time.time())
        np.random.seed(self.seed)

    def run(self):
        self.avg_obj_val = 0.0
        self.avg_obj_val_eval = np.zeros(self.num_evals)
        for r in range(self.num_runs):
            eval_count = 0
            best_so_far = sys.float_info.max
            curr_pop, curr_obj_vals = self.init()
            while eval_count < self.num_evals:
                # 1. evaluation
                curr_obj_vals = self.evaluate(curr_pop, self.dist)
                self.update_best_sol(curr_pop, curr_obj_vals)
                for i in range(self.pop_size):
                    if best_so_far > curr_obj_vals[i]:
                        best_so_far = curr_obj_vals[i]
                    if eval_count < self.num_evals:
                        self.avg_obj_val_eval[eval_count] += best_so_far
                        eval_count += 1
                # 2. determination
                curr_pop = self.tournament_select(curr_pop, curr_obj_vals, self.num_players)
                # 3. transition
                curr_pop = self.crossover(curr_pop, self.crossover_rate)
                curr_pop = self.mutate(curr_pop, self.mutation_rate)
            self.avg_obj_val += best_so_far
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
            for i in range(self.num_patterns_sol):
                r = curr_pop[p][i]
                s = curr_pop[p][(i+1) % self.num_patterns_sol]
                tour_dist[p] += self.dist[r][s]
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

    def crossover(self, curr_pop, cr):
        tmp_pop = curr_pop.copy()
        mid = self.pop_size // 2
        ssz = self.num_patterns_sol
        for i in range(mid):
            f = np.random.rand()
            if f <= cr:
                # 1. one-point crossover
                xp = np.random.randint(ssz)
                s1 = tmp_pop[i]
                s2 = tmp_pop[mid+i]
                s1[xp:], s2[xp:] = s2[xp:], s1[xp:]
                # 2. correct the solutions
                for j in range(i, self.pop_size, mid):
                    s = tmp_pop[j]
                    # find the number of times each city was visited,
                    # which can be either 0, 1, or 2; i.e., not visited,
                    # visited once, and visited twice
                    visit = np.zeros(ssz, dtype=int)
                    for k in range(ssz):
                        visit[s[k]] += 1
                    # put cities not visited in bag
                    bag = []
                    for k in range(ssz):
                        if visit[k] == 0:
                            bag.append(k)
                    # correct cities visited twice, by replacing one
                    # of which by one randomly chosen from the bag, if
                    # necessary
                    if len(bag) > 0:
                        bag = np.array(bag)
                        np.random.shuffle(bag)
                        n = 0
                        for k in range(xp, ssz):
                            if visit[s[k]] == 2:
                                s[k] = bag[n]
                                n += 1
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
        print("# seed: %s" % self.seed)

def usage():
    lib.usage("<filename_ins> <pop_size> <cr> <mr> <#players>")

if __name__ == "__main__":
    if ac() == 2 and ss(1) == "-h": usage()
    elif ac() == 1: search = ga()
    elif ac() == 10: search = ga(si(1), si(2), si(3), ss(4), ss(5), si(6), sf(7), sf(8), si(9))
    else: usage()
    lib.run(search, None)
