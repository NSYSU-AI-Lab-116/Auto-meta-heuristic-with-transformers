#!/usr/bin/env python
import numpy as np; import time; import sys; import os
from lib import *

class ga:
    def __init__(self, num_runs = 3, num_evals = 1000, num_patterns_sol = 10, filename_ini = "", pop_size = 10, crossover_rate = 0.6, mutation_rate = 0.01, num_players = 3):
        self.num_runs = num_runs
        self.num_evals = num_evals
        self.num_patterns_sol = num_patterns_sol
        self.filename_ini = filename_ini
        self.pop_size = pop_size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.num_players = num_players
        self.best_obj_val = 0.0
        self.best_sol = None
        self.seed = int(time.time())
        np.random.seed(self.seed)

    def run(self):
        avg_obj_val = 0.0
        avg_obj_val_eval = np.zeros(self.num_evals)
        for r in range(self.num_runs):
            eval_count = 0
            best_so_far = 0.0
            # 0. initialization
            curr_pop = self.init()
            while eval_count < self.num_evals:
                # 1. evaluation
                curr_obj_vals = self.evaluate(curr_pop)
                self.update_best_sol(curr_pop, curr_obj_vals)
                for i in range(self.pop_size):
                    if best_so_far < curr_obj_vals[i]:
                        best_so_far = curr_obj_vals[i]
                    if eval_count < self.num_evals:
                        avg_obj_val_eval[eval_count] += best_so_far
                        eval_count += 1
                # 2. determination
                curr_pop = self.select(curr_pop, curr_obj_vals, self.num_players)
                # 3. transition
                curr_pop = self.crossover(curr_pop, self.crossover_rate)
                curr_pop = self.mutation(curr_pop, self.mutation_rate)
            avg_obj_val += self.best_obj_val
        # 4. output
        avg_obj_val /= self.num_runs
        for i in range(self.num_evals):
            avg_obj_val_eval[i] /= self.num_runs
            print("%.3f" % avg_obj_val_eval[i])
        return curr_pop

    def init(self):
        if len(self.filename_ini) == 0:
            curr_pop = np.array([np.array([1 if x >= 0.5 else 0 for x in np.random.rand(self.num_patterns_sol)]) for i in range(self.pop_size)])
        else:
            with open(self.filename_ini, "r") as f:
                curr_pop = np.array(f.read().strip().split(), dtype=int).reshape(self.pop_size, self.num_patterns_sol)
        self.best_obj_val = 0
        return curr_pop

    def evaluate(self, curr_pop):
        return np.array(list(map(sum, curr_pop)))

    def select(self, curr_pop, curr_obj_vals, num_players):
        tmp_pop = []
        for i in range(self.pop_size):
            k = np.random.randint(self.pop_size)
            f = curr_obj_vals[k]
            for j in range(1, num_players):
                n = np.random.randint(self.pop_size)
                if curr_obj_vals[n] > f:
                    k = n
                    f = curr_obj_vals[k]
            tmp_pop.append(curr_pop[k].copy())
        return tmp_pop

    def update_best_sol(self, curr_pop, curr_obj_vals):
        for i in range(self.pop_size):
            if curr_obj_vals[i] > self.best_obj_val:
                self.best_obj_val = curr_obj_vals[i]
                self.best_sol = curr_pop[i]

    def crossover(self, curr_pop, cr):
        mid = int(self.pop_size / 2)
        for i in range(mid):
            f = np.random.rand()
            if f <= cr:
                xp = np.random.randint(self.num_patterns_sol)
                for j in range(xp, self.num_patterns_sol):
                    curr_pop[i][j], curr_pop[mid+i][j] = curr_pop[mid+i][j], curr_pop[i][j]
        return curr_pop

    def mutation(self, curr_pop, mr):
        for i in range(self.pop_size):
            for j in range(self.num_patterns_sol):
                f = np.random.rand()
                if f <= mr:
                    curr_pop[i][j] ^= 1
        return curr_pop

    def print_parameters(self, algname):
        print("# name of the search algorithm: '%s'" % algname)
        print("# number of runs: %s" % self.num_runs)
        print("# number of evaluations: %s" % self.num_evals)
        print("# number of patterns: %s" % self.num_patterns_sol)
        print("# filename of the initial seeds: '%s'" % self.filename_ini)
        print("# population size: %s" % self.pop_size)
        print("# crossover rate: %s" % self.crossover_rate)
        print("# mutation rate: %s" % self.mutation_rate)
        print("# number of players: %s" % self.num_players)
        print("# seed: %s" % self.seed)

def usage():
    lib.usage("<pop_size> <cr> <mr> <#players>")

if __name__ == "__main__":
    if ac() == 2 and ss(1) == "-h": usage()
    elif ac() == 1: search = ga()
    elif ac() == 9: search = ga(si(1), si(2), si(3), ss(4), si(5), sf(6), sf(7), si(8))
    else: usage()
    lib.run(search, lib.print_population)
