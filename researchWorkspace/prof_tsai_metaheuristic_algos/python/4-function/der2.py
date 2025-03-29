#!/usr/bin/env python
import numpy as np; import time; import sys; import os; import functions
from lib import *
from de import de

class der2(de):
    def __init__(self, num_runs = 3, num_evals = 1000, num_dims = 2, filename_ini = "", filename_ins = "mvfAckley", pop_size = 10, F = 0.7, cr = 0.5, v_min = -32.0, v_max = 32.0):
        super().__init__(num_runs, num_evals, num_dims, filename_ini, filename_ins, pop_size, F, cr, v_min, v_max)

    def mutate(self, curr_pop):
        new_pop = np.zeros((self.pop_size, self.num_dims))
        for i in range(self.pop_size):
            s1 = curr_pop[np.random.randint(self.pop_size)]
            s2 = curr_pop[np.random.randint(self.pop_size)]
            s3 = curr_pop[np.random.randint(self.pop_size)]
            s4 = curr_pop[np.random.randint(self.pop_size)]
            s5 = curr_pop[np.random.randint(self.pop_size)]
            new_pop[i] = np.clip(s1 + self.F * (s2 - s3) + self.F * (s4 - s5), self.v_min, self.v_max)
        return new_pop

def usage():
    lib.usage("<#runs> <#evals> <#dims> <filename_ini> <filename_ins> <pop_size> <F> <cr> <v_min> <v_max>", common_params = "")

if __name__ == "__main__":
    if ac() == 2 and ss(1) == "-h": usage()
    elif ac() == 1: search = der2()
    elif ac() == 11: search = der2(si(1), si(2), si(3), ss(4), ss(5), si(6), sf(7), sf(8), sf(9), sf(10))
    else: usage()
    lib.run(search, lib.print_solution)
