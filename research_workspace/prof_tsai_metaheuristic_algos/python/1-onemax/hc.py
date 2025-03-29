#!/usr/bin/env python
import numpy as np; import time; import sys; import os
from lib import *

class hc:
    def __init__(self, num_runs = 3, num_evals = 1000, num_patterns_sol = 10, filename_ini = ""):
        self.num_runs = num_runs
        self.num_evals = num_evals
        self.num_patterns_sol = num_patterns_sol
        self.filename_ini = filename_ini
        self.seed = int(time.time())
        np.random.seed(self.seed)

    def run(self):
        avg_obj_val = 0.0
        avg_obj_val_eval = np.zeros(self.num_evals)
        for r in range(self.num_runs):
            # 0. Initialization
            sol, obj_val = self.init()
            eval_count = 0
            avg_obj_val_eval[eval_count] += obj_val
            eval_count += 1
            while eval_count < self.num_evals:
                # 1. Transition
                tmp_sol = self.transit(sol)
                # 2. Evaluation
                tmp_obj_val = self.evaluate(tmp_sol)
                # 3. Determination
                sol, obj_val = self.determine(tmp_sol, tmp_obj_val, sol, obj_val)
                avg_obj_val_eval[eval_count] += obj_val
                eval_count += 1
            avg_obj_val += obj_val
        # 4. Output
        avg_obj_val /= self.num_runs
        for i in range(self.num_evals):
            avg_obj_val_eval[i] /= self.num_runs
            print("%.3f" % avg_obj_val_eval[i])
        return '{0:0{1}b}'.format(sol, self.num_patterns_sol)

    def init(self):
        if len(self.filename_ini) == 0:
            sol = np.random.randint(2, size = self.num_patterns_sol, dtype=int)
        else:
            with open(self.filename_ini, "r") as f:
                sol = np.array(f.read().strip().split(), dtype=int)
        sol = int(sol.dot(2**np.arange(sol.size)[::-1]))
        obj_val = self.evaluate(sol)
        return sol, obj_val

    def transit(self, s):
        if s == 0 or s == (1 << self.num_patterns_sol) - 1:
            return s
        s += 1 if np.random.rand() < 0.5 else -1
        return s

    def evaluate(self, s):
        return bin(s).count("1")

    def determine(self, v, fv, s, fs):
        return (v, fv) if fv > fs else (s, fs)

    def print_parameters(self, algname):
        print("# name of the search algorithm: '%s'" % algname)
        print("# number of runs: %s" % self.num_runs)
        print("# number of evaluations: %s" % self.num_evals)
        print("# number of patterns: %s" % self.num_patterns_sol)
        print("# filename of the initial seeds: '%s'" % self.filename_ini)
        print("# seed: %s" % self.seed)

def usage():
    lib.usage("")

if __name__ == "__main__":
    if ac() == 2 and ss(1) == "-h": usage()
    elif ac() == 1: search = hc()
    elif ac() == 5: search = hc(si(1), si(2), si(3), ss(4))
    else: usage()
    lib.run(search, lib.print_solution)
