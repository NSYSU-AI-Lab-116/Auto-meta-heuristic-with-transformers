#!/usr/bin/env python
import numpy as np; import time; import sys; import os
from lib import *
from ga import ga

class gaxu(ga):
    def __init__(self, num_runs = 3, num_evals = 1000, num_patterns_sol = 10, filename_ini = "", pop_size = 10, crossover_rate = 0.6, mutation_rate = 0.01, num_players = 0):
        super().__init__(num_runs, num_evals, num_patterns_sol, filename_ini, pop_size, crossover_rate, mutation_rate, num_players)

    def crossover(self, curr_pop, cr):
        # uniform crossover
        mid = self.pop_size // 2
        for i in range(mid):
            for j in range(self.num_patterns_sol):
                f = np.random.rand()
                if f <= 0.5: # yes, 0.5 instead of cr
                    curr_pop[i][j], curr_pop[mid+i][j] = curr_pop[mid+i][j], curr_pop[i][j]
        return curr_pop

def usage():
    lib.usage("<pop_size> <cr> <mr> <#players>")

if __name__ == "__main__":
    if ac() == 2 and ss(1) == "-h": usage()
    elif ac() == 1: search = gaxu()
    elif ac() == 9: search = gaxu(si(1), si(2), si(3), ss(4), si(5), sf(6), sf(7), si(8))
    else: usage()
    lib.run(search, lib.print_population)
