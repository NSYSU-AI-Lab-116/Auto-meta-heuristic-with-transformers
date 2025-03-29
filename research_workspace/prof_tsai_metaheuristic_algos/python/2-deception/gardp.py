#!/usr/bin/env python
import numpy as np; import time; import sys; import os
from lib import *
from gar import gar

class gardp(gar):
    def __init__(self, num_runs = 3, num_evals = 1000, num_patterns_sol = 10, filename_ini = "", pop_size = 10, crossover_rate = 0.6, mutation_rate = 0.01, num_players = 0):
        super().__init__(num_runs, num_evals, num_patterns_sol, filename_ini, pop_size, crossover_rate, mutation_rate, num_players)

    def evaluate(self, curr_pop):
        n = np.zeros(self.pop_size)
        for i in range(self.pop_size):
            sol = curr_pop[i]
            n[i] = abs(int(sol.dot(2**np.arange(sol.size)[::-1])) - (1 << (sol.size - 2)))
        return n

def usage():
    lib.usage("<pop_size> <cr> <mr> <#players>")

if __name__ == "__main__":
    if ac() == 2 and ss(1) == "-h": usage()
    elif ac() == 1: search = gardp()
    elif ac() == 9: search = gardp(si(1), si(2), si(3), ss(4), si(5), sf(6), sf(7), si(8))
    else: usage()
    lib.run(search, lib.print_population)
