#!/usr/bin/env python
import numpy as np; import time; import sys; import os
from lib import *

class ts:
    def __init__(self, num_runs = 3, num_evals = 1000, num_patterns_sol = 10, filename_ini = "", num_neighbors = 3, siz_tabulist = 7):
        self.num_runs = num_runs
        self.num_evals = num_evals
        self.num_patterns_sol = num_patterns_sol
        self.filename_ini = filename_ini
        self.num_neighbors = num_neighbors
        self.siz_tabulist = siz_tabulist
        self.eval_count = 0
        self.tabulist = []
        self.seed = int(time.time())
        np.random.seed(self.seed)

    def run(self):
        avg_obj_val = 0.0
        avg_obj_val_eval = np.zeros(self.num_evals)
        for r in range(self.num_runs):
            # 0. initialization
            obj_val, sol, best_obj_val, best_sol = self.init()
            self.eval_count = 0
            avg_obj_val_eval[self.eval_count] += obj_val
            while self.eval_count < self.num_evals-1:
                # 1. transition and evaluation
                tmp_sol, tmp_obj_val, n_evals = self.select_neighbor_not_in_tabu(sol)
                if n_evals > 0:
                    # 2. determination
                    if tmp_obj_val > obj_val:
                        obj_val, sol = tmp_obj_val, tmp_sol
                    if obj_val > best_obj_val:
                        best_obj_val, best_sol = obj_val, sol
                    avg_obj_val_eval[self.eval_count] += best_obj_val
                    for i in range(1, n_evals):
                        avg_obj_val_eval[self.eval_count - i] = avg_obj_val_eval[self.eval_count]
            avg_obj_val += best_obj_val
        # 4. output
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
        self.tabulist.clear()
        return obj_val, sol, obj_val, sol

    def transit(self, sol):
        t = sol.copy()
        i = np.random.randint(len(sol))
        t[i] ^= 1
        return t

    def select_neighbor_not_in_tabu(self, sol):
        t, f_t, n_evals = None, 0, 0
        for i in range(self.num_neighbors):
            v = self.transit(sol)
            if not self.in_tabu(v):
                n_evals += 1
                f_v = self.evaluate(v)
                if f_v > f_t:
                    t, f_t = v, f_v
                if self.eval_count >= self.num_evals-1:
                    break
        if n_evals > 0:
            self.append_to_tabu_list(t)
        return t, f_t, n_evals

    def in_tabu(self, sol):
        for s in self.tabulist:
            if np.array_equal(s, sol):
                return True
        return False

    def evaluate(self, sol):
        self.eval_count += 1
        return sum(sol)

    def append_to_tabu_list(self, sol):
        self.tabulist.append(sol)
        if len(self.tabulist) > self.siz_tabulist:
            self.tabulist.pop(0)

    def print_parameters(self, algname):
        print("# name of the search algorithm: '%s'" % algname)
        print("# number of runs: %s" % self.num_runs)
        print("# number of evaluations: %s" % self.num_evals)
        print("# number of patterns: %s" % self.num_patterns_sol)
        print("# filename of the initial seeds: '%s'" % self.filename_ini)
        print("# number of neighbors: %s" % self.num_neighbors)
        print("# size of the tabu list: %s" % self.siz_tabulist)
        print("# seed: %s" % self.seed)

def usage():
    lib.usage("<#neighbors> <tabulist_size>")

if __name__ == "__main__":
    if ac() == 2 and ss(1) == "-h": usage()
    elif ac() == 1: search = ts()
    elif ac() == 7: search = ts(si(1), si(2), si(3), ss(4), si(5), si(6))
    else: usage()
    lib.run(search, lib.print_solution)
