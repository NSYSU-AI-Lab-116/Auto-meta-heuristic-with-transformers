#!/usr/bin/env python
import numpy as np; import time; import sys; import os
from lib import *
from ts import ts

class tsdp(ts):
    def __init__(self, num_runs = 3, num_evals = 1000, num_patterns_sol = 10, filename_ini = "", num_neighbors = 3, siz_tabulist = 7):
        super().__init__(num_runs, num_evals, num_patterns_sol, filename_ini, num_neighbors, siz_tabulist)

    def evaluate(self, sol):
        self.eval_count += 1
        return abs(int(sol.dot(2**np.arange(sol.size)[::-1])) - (1 << (sol.size - 2)))

    def select_neighbor_not_in_tabu(self, sol):
        t, f_t, n_evals = super().select_neighbor_not_in_tabu(sol)
        if n_evals == 0:
            while (True):
                t = np.random.randint(2, size = len(sol))
                if not self.in_tabu(t):
                    break
            self.append_to_tabu_list(t)
            f_t = self.evaluate(t)
            n_evals = 1
        return t, f_t, n_evals

def usage():
    lib.usage("<#neighbors> <tabulist_size>")

if __name__ == "__main__":
    if ac() == 2 and ss(1) == "-h": usage()
    elif ac() == 1: search = tsdp()
    elif ac() == 7: search = tsdp(si(1), si(2), si(3), ss(4), si(5), si(6))
    else: usage()
    lib.run(search, lib.print_solution)
