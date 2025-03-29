#!/usr/bin/env python
import numpy as np; import time; import sys; import os
from lib import *
from sa import sa

class sadp(sa):
    def __init__(self, num_runs = 3, num_evals = 20000, num_patterns_sol = 4, filename_ini = "", min_temp = 0.00001, max_temp = 1.0):
        super().__init__(num_runs, num_evals, num_patterns_sol, filename_ini, min_temp, max_temp)

    def evaluate(self, sol):
        return abs(int(sol.dot(2**np.arange(sol.size)[::-1])) - (1 << (sol.size - 2)))

def usage():
    lib.usage("<min_temp> <max_temp>")

if __name__ == "__main__":
    if ac() == 2 and ss(1) == "-h": usage()
    elif ac() == 1: search = sadp()
    elif ac() == 7: search = sadp(si(1), si(2), si(3), ss(4), sf(5), sf(6))
    else: usage()
    lib.run(search, lib.print_solution)
