#!/usr/bin/env python
import numpy as np; import time; import sys; import os
from lib import *

class sa:
    def __init__(self, num_runs = 3, num_evals = 1000, num_patterns_sol = 10, filename_ini = "", min_temp = 0.00001, max_temp = 1.0):
        self.num_runs = num_runs
        self.num_evals = num_evals
        self.num_patterns_sol = num_patterns_sol
        self.filename_ini = filename_ini
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.seed = int(time.time())
        np.random.seed(self.seed)

    def run(self):
        avg_obj_val = 0.0
        avg_obj_val_eval = np.zeros(self.num_evals)
        for r in range(self.num_runs):
            # 0. Initialization
            obj_val, sol, best_obj_val, best_sol, curr_temp = self.init()
            eval_count = 0
            avg_obj_val_eval[eval_count] += obj_val
            eval_count += 1
            while eval_count < self.num_evals:
                # 1. Transition
                tmp_sol = self.transit(sol)
                # 2. Evaluation
                tmp_obj_val = self.evaluate(tmp_sol)
                # 3. Determination
                if self.determine(tmp_obj_val, obj_val, curr_temp):
                    obj_val, sol = tmp_obj_val, tmp_sol
                if obj_val > best_obj_val:
                    best_obj_val, best_sol = obj_val, sol
                curr_temp = self.annealing(curr_temp)
                avg_obj_val_eval[eval_count] += best_obj_val
                eval_count += 1
            avg_obj_val += best_obj_val
        # 4. Output
        avg_obj_val /= self.num_runs
        for i in range(self.num_evals):
            avg_obj_val_eval[i] /= self.num_runs
            print("%.3f" % avg_obj_val_eval[i])
        return best_sol

    def init(self):
        if len(self.filename_ini) == 0:
            sol = np.array([1 if x >= 0.5 else 0 for x in np.random.rand(self.num_patterns_sol)])
        else:
            with open(self.filename_ini, "r") as f:
                sol = np.array(f.read().strip().split(), dtype=int)
        obj_val = self.evaluate(sol)
        return obj_val, sol, obj_val, sol, self.max_temp

    def transit(self, sol):
        t = sol.copy()
        i = np.random.randint(len(sol))
        t[i] ^= 1
        return t

    def evaluate(self, sol):
        return sum(sol)

    def determine(self, tmp_obj_val, obj_val, temperature):
        r = np.random.rand()
        p = np.exp((tmp_obj_val - obj_val) / temperature)
        return r < p

    def annealing(self, temperature):
        return 0.9 * temperature

    def print_parameters(self, algname):
        print("# name of the search algorithm: '%s'" % algname)
        print("# number of runs: %s" % self.num_runs)
        print("# number of evaluations: %s" % self.num_evals)
        print("# number of patterns: %s" % self.num_patterns_sol)
        print("# filename of the initial seeds: '%s'" % self.filename_ini)
        print("# minimum temperature: %s" % self.min_temp)
        print("# maximum temperature: %s" % self.max_temp)
        print("# seed: %s" % self.seed)

def usage():
    lib.usage("<min_temp> <max_temp>")

if __name__ == "__main__":
    if ac() == 2 and ss(1) == "-h": usage()
    elif ac() == 1: search = sa()
    elif ac() == 7: search = sa(si(1), si(2), si(3), ss(4), sf(5), sf(6))
    else: usage()
    lib.run(search, lib.print_solution)
