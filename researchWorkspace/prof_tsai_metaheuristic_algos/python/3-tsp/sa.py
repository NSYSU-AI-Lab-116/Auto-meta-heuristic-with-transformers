#!/usr/bin/env python
import numpy as np; import time; import sys; import os
from lib import *

class sa:
    def __init__(self, num_runs, num_evals, num_patterns_sol, filename_ini, max_temp, min_temp, dist, continue_flag, total_evals):
        self.num_runs = num_runs
        self.num_evals = num_evals
        self.num_patterns_sol = num_patterns_sol
        self.filename_ini = filename_ini
        self.max_temp = max_temp
        self.min_temp = min_temp
        self.dist = dist
        self.continue_flag = continue_flag
        self.total_evals = total_evals
        self.seed = int(time.time())
        # np.random.seed(self.seed)

    def run(self, sol_orig, eval_count_orig, avg_obj_val_eval_orig, best_obj_val_orig, best_sol_orig):
        eval_count_saved = eval_count_orig
        for r in range(self.num_runs):
            eval_count = eval_count_saved
            # 0. Initialization
            curr_sol = self.init(sol_orig)
            curr_temp = self.max_temp
            best_obj_val = best_obj_val_orig
            best_sol = best_sol_orig
            curr_sol = sol_orig
            obj_val = self.evaluate(curr_sol, self.dist)
            while eval_count < min(self.total_evals, eval_count_saved + self.num_evals):
                # 1. Transition
                tmp_sol = self.transit(curr_sol)
                # 2. Evaluation
                tmp_obj_val = self.evaluate(tmp_sol, self.dist)
                # 3. Determination
                if self.determine(tmp_obj_val, obj_val, curr_temp):
                    obj_val, curr_sol = tmp_obj_val, tmp_sol
                if obj_val < best_obj_val:
                    best_obj_val, best_sol = obj_val, curr_sol
                curr_temp = self.annealing(curr_temp)
                avg_obj_val_eval_orig[eval_count] += best_obj_val
                eval_count += 1
            eval_count_orig = eval_count
            if best_obj_val < best_obj_val_orig:
                best_obj_val_orig = best_obj_val
                best_sol_orig = best_sol
                sol_orig = best_sol
            else:
                sol_orig = curr_sol
        return sol_orig, eval_count_orig, avg_obj_val_eval_orig, best_obj_val_orig, best_sol_orig

    def init(self, sol):
        if not self.continue_flag:
            sol = np.arange(len(sol))
            np.random.shuffle(sol)
        return sol

    def transit(self, sol):
        t = sol.copy()
        ssz = len(sol)
        i = np.random.randint(ssz)
        j = np.random.randint(ssz)
        t[i], t[j] = t[j], t[i]
        return t

    def evaluate(self, sol, dist):
        tour_dist = 0.0
        ssz = len(sol)
        for i in range(ssz):
            r = sol[i]
            s = sol[(i+1) % ssz]
            tour_dist += dist[r][s]
        return tour_dist

    def determine(self, tmp_obj_val, obj_val, temperature):
        r = np.random.rand()
        p = np.exp((tmp_obj_val - obj_val) / temperature)
        return r > p

    def annealing(self, temperature):
        return 0.9 * temperature

    def print_parameters(self, algname):
        print("# name of the search algorithm: '%s'" % algname)
        print("# number of runs: %s" % self.num_runs)
        print("# number of evaluations: %s" % self.num_evals)
        print("# number of patterns: %s" % self.num_patterns_sol)
        print("# filename of the initial seeds: '%s'" % self.filename_ini)
        print("# maximum temperature: %s" % self.max_temp)
        print("# minimum temperature: %s" % self.min_temp)
        print("# dist: %s" % self.dist)
        print("# continue_flag: %s" % self.continue_flag)
        print("# seed: %s" % self.seed)

if __name__ == "__main__":
    pass
