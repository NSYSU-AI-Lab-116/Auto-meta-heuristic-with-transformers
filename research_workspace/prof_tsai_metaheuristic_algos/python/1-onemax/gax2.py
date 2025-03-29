#!/usr/bin/env python
import numpy as np; import time; import sys; import os
from lib import *
from ga import ga

class gax2(ga):
    def __init__(self, num_runs = 3, num_evals = 1000, num_patterns_sol = 10, filename_ini = "", pop_size = 10, crossover_rate = 0.6, mutation_rate = 0.01, num_players = 0):
        super().__init__(num_runs, num_evals, num_patterns_sol, filename_ini, pop_size, crossover_rate, mutation_rate, num_players)

    def crossover(self, curr_pop, cr):
        # two-point crossover
        mid = self.pop_size // 2
        for i in range(mid):
            f = np.random.rand()
            if f <= cr:
                xp1 = np.random.randint(self.num_patterns_sol)
                xp2 = np.random.randint(self.num_patterns_sol)
                if xp2 < xp1:
                    xp1, xp2 = xp2, xp1
                for j in range(xp1, xp2):
                    curr_pop[i][j], curr_pop[mid+i][j] = curr_pop[mid+i][j], curr_pop[i][j]
        return curr_pop

def usage():
    lib.usage("<pop_size> <cr> <mr> <#players>")

if __name__ == "__main__":
    if ac() == 2 and ss(1) == "-h": usage()
    elif ac() == 1: search = gax2()
    elif ac() == 9: search = gax2(si(1), si(2), si(3), ss(4), si(5), sf(6), sf(7), si(8))
    else: usage()
    lib.run(search, lib.print_population)
