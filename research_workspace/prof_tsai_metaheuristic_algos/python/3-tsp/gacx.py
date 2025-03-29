#!/usr/bin/env python
import numpy as np; import time; import sys; import os; import math
from lib import *
from ga import ga

class gacx(ga):
    def __init__(self, num_runs = 3, num_evals = 120000, num_patterns_sol = 1002, filename_ini = "", filename_ins = "pr1002.tsp", pop_size = 120, crossover_rate = 0.4, mutation_rate = 0.1, num_players = 3):
        super().__init__(num_runs, num_evals, num_patterns_sol, filename_ini, filename_ins, pop_size, crossover_rate, mutation_rate, num_players)

    def crossover(self, curr_pop, cr):
        tmp_pop = curr_pop.copy()
        mid = self.pop_size // 2
        ssz = self.num_patterns_sol
        for i in range(mid):
            f = np.random.rand()
            if f <= cr:
                mask = np.zeros(ssz, dtype=bool)
                c1 = i
                c2 = i+mid
                c = tmp_pop[c1][0]
                n = tmp_pop[c2][0]
                mask[0] = True
                try:
                    while c != n:
                        for j in range(ssz):
                            if n == tmp_pop[c1][j]:
                                if mask[j]:
                                    raise StopIteration
                                c = n
                                n = tmp_pop[c2][j]
                                mask[j] = True
                                break
                except StopIteration:
                    for j in range(ssz):
                        if not mask[j]:
                            tmp_pop[c1][j], tmp_pop[c2][j] = tmp_pop[c2][j], tmp_pop[c1][j]
        return tmp_pop

def usage():
    lib.usage("<filename_ins> <pop_size> <cr> <mr> <#players>")

if __name__ == "__main__":
    if ac() == 2 and ss(1) == "-h": usage()
    elif ac() == 1: search = gacx()
    elif ac() == 10: search = gacx(si(1), si(2), si(3), ss(4), ss(5), si(6), sf(7), sf(8), si(9))
    else: usage()
    lib.run(search, None)
