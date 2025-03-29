#!/usr/bin/env python
import numpy as np; import time; import sys; import os
from lib import *
from ga import ga

class gar(ga):
    def __init__(self, num_runs = 3, num_evals = 1000, num_patterns_sol = 10, filename_ini = "", pop_size = 10, crossover_rate = 0.6, mutation_rate = 0.01, num_players = 0):
        super().__init__(num_runs, num_evals, num_patterns_sol, filename_ini, pop_size, crossover_rate, mutation_rate, num_players)

    def select(self, curr_pop, curr_obj_vals, num_players):
        # 1. compute the probabilities of the roulette wheel
        total = sum(curr_obj_vals)
        tmp_pop = []
        for i in range(self.pop_size):
            # 2. select the individuals for the next generation
            f = total * np.random.rand()
            for j in range(self.pop_size):
                f -= curr_obj_vals[j]
                if f <= 0.0:
                    tmp_pop.append(curr_pop[j].copy())
                    break
        return tmp_pop

def usage():
    lib.usage("<pop_size> <cr> <mr> <#players>")

if __name__ == "__main__":
    if ac() == 2 and ss(1) == "-h": usage()
    elif ac() == 1: search = gar()
    elif ac() == 9: search = gar(si(1), si(2), si(3), ss(4), si(5), sf(6), sf(7), si(8))
    else: usage()
    lib.run(search, lib.print_population)
