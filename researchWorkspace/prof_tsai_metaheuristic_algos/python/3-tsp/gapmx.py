#!/usr/bin/env python
import numpy as np; import time; import sys; import os; import math
from lib import *
from ga import ga

class gapmx(ga):
    def __init__(self, num_runs = 3, num_evals = 120000, num_patterns_sol = 1002, filename_ini = "", filename_ins = "pr1002.tsp", pop_size = 120, crossover_rate = 0.4, mutation_rate = 0.1, num_players = 3):
        super().__init__(num_runs, num_evals, num_patterns_sol, filename_ini, filename_ins, pop_size, crossover_rate, mutation_rate, num_players)

    def crossover(self, curr_pop, cr):
        # originally crossover_ox, renamed for override
        tmp_pop = curr_pop.copy()
        mid = self.pop_size // 2
        ssz = self.num_patterns_sol
        for i in range(mid):
            # 1. select the two parents and offspring
            f = np.random.rand()
            if f <= cr:
                # 1. select the two parents and offspring
                p = [ i, i+mid ]
                # 2. select the mapping sections
                xp1 = np.random.randint(ssz + 1)
                xp2 = np.random.randint(ssz + 1)
                if xp1 > xp2:
                    xp1, xp2 = xp2, xp1
                # 3. swap the mapping sections
                for j in range(xp1, xp2):
                    tmp_pop[p[0]][j], tmp_pop[p[1]][j] = tmp_pop[p[1]][j], tmp_pop[p[0]][j]
                # 4. fix the duplicates
                for k in range(2):
                    z = p[k]
                    for j in range(ssz):
                        if j < xp1 or j >= xp2:
                            c = curr_pop[z][j]
                            m = xp1
                            while m < xp2:
                                if c == tmp_pop[z][m]:
                                    c = curr_pop[z][m]
                                    m = xp1     # restart the while loop
                                else:
                                    m += 1      # move on to the next
                            if c != curr_pop[z][j]:
                                tmp_pop[z][j] = c
        return tmp_pop

def usage():
    lib.usage("<filename_ins> <pop_size> <cr> <mr> <#players>")

if __name__ == "__main__":
    if ac() == 2 and ss(1) == "-h": usage()
    elif ac() == 1: search = gapmx()
    elif ac() == 10: search = gapmx(si(1), si(2), si(3), ss(4), ss(5), si(6), sf(7), sf(8), si(9))
    else: usage()
    lib.run(search, None)
