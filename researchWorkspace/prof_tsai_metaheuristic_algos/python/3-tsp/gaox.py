#!/usr/bin/env python
import numpy as np; import time; import sys; import os; import math
from lib import *
from ga import ga

class gaox(ga):
    def __init__(self, num_runs = 3, num_evals = 120000, num_patterns_sol = 1002, filename_ini = "", filename_ins = "pr1002.tsp", pop_size = 120, crossover_rate = 0.4, mutation_rate = 0.1, num_players = 3):
        super().__init__(num_runs, num_evals, num_patterns_sol, filename_ini, filename_ins, pop_size, crossover_rate, mutation_rate, num_players)

    def crossover(self, curr_pop, cr):
        # originally crossover_ox, renamed for override
        tmp_pop = curr_pop.copy()
        mid = self.pop_size // 2
        ssz = self.num_patterns_sol
        for i in range(mid):
            f = np.random.rand()
            if f <= cr:
                # 1. create the mapping sections
                xp1 = np.random.randint(ssz + 1)
                xp2 = np.random.randint(ssz + 1)
                if xp1 > xp2:
                    xp1, xp2 = xp2, xp1
                # 2. indices to the two parents and offspring
                p = [ i, i+mid ]
                # 3. the main process of ox
                for k in range(2):
                    c1 = p[k]
                    c2 = p[1-k]
                    # 4. mask the genes between xp1 and xp2
                    s1 = curr_pop[c1]
                    s2 = curr_pop[c2]
                    msk1 = np.zeros(ssz, dtype=bool)
                    for j in range(xp1, xp2):
                        msk1[s1[j]] = True
                    msk2 = np.zeros(ssz, dtype=bool)
                    for j in range(0, ssz):
                        msk2[j] = msk1[s2[j]]
                    # 5. replace the genes that are not masked
                    j = xp2 % ssz
                    for z in range(ssz):
                        if not msk2[z]:
                            tmp_pop[c1][j] = s2[z]
                            j = (j+1) % ssz
        return tmp_pop

def usage():
    lib.usage("<filename_ins> <pop_size> <cr> <mr> <#players>")

if __name__ == "__main__":
    if ac() == 2 and ss(1) == "-h": usage()
    elif ac() == 1: search = gaox()
    elif ac() == 10: search = gaox(si(1), si(2), si(3), ss(4), ss(5), si(6), sf(7), sf(8), si(9))
    else: usage()
    lib.run(search, None)
