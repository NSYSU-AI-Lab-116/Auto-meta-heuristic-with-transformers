#!/usr/bin/env python
import numpy as np; import time; import sys; import os
from lib import *

class sa_refinit:
    def __init__(self, num_runs = 3, num_evals = 1000, num_patterns_sol = 10, filename_ini = "", min_temp = 0.00001, max_temp = 1.0, num_samplings = 10, num_same_bits = 2):
        self.num_runs = num_runs
        self.num_evals = num_evals
        self.num_patterns_sol = num_patterns_sol
        self.filename_ini = filename_ini
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.num_samplings = num_samplings
        self.num_same_bits = num_same_bits
        self.seed = int(time.time())
        np.random.seed(self.seed)

    def run(self):
        avg_obj_val = 0.0
        avg_obj_val_eval = np.zeros(self.num_evals)
        for r in range(self.num_runs):
            # 0. Initialization
            obj_val, sol, best_obj_val, best_sol, curr_temp = self.init(avg_obj_val_eval)
            eval_count = self.num_samplings
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

    def init(self, avg_obj_val_eval):
        if len(self.filename_ini) > 0:
            with open(self.filename_ini, "r") as f:
                sol = np.array(f.read().strip().split(), dtype=int)
        else:
            tmp_sol = np.zeros(self.num_patterns_sol, dtype=int)
            for j in range(self.num_samplings):
                for i in range(0, self.num_patterns_sol, self.num_same_bits):
                    tmp_sol[i:i+self.num_same_bits] = np.random.randint(2, size = self.num_same_bits)
                tmp_obj_val = self.evaluate(tmp_sol)
                if j == 0 or tmp_obj_val > obj_val:
                    best_obj_val = obj_val = tmp_obj_val
                    sol = tmp_sol
                avg_obj_val_eval[j] += obj_val
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
        print("# name of the search algorithm: 'sa_refinit'")
        print("# number of runs: %s" % self.num_runs)
        print("# number of evaluations: %s" % self.num_evals)
        print("# number of patterns: %s" % self.num_patterns_sol)
        print("# filename of the initial seeds: '%s'" % self.filename_ini)
        print("# minimum temperature: %s" % self.min_temp)
        print("# maximum temperature: %s" % self.max_temp)
        print("# number of samples: %s" % self.num_samplings)
        print("# number of same bits: %s" % self.num_same_bits)
        print("# seed: %s" % self.seed)

def usage():
    lib.usage("<min_temp> <max_temp> <#samples> <#same_bits>")

if __name__ == "__main__":
    if ac() == 2 and ss(1) == "-h": usage()
    elif ac() == 1: search = sa_refinit()
    elif ac() == 9: search = sa_refinit(si(1), si(2), si(3), ss(4), sf(5), sf(6), si(7), si(8))
    else: usage()
    lib.run(search, lib.print_solution)
