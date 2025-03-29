#!/usr/bin/env python
import numpy as np; import time; import sys; import os
from lib import *
from hcdp_r import hcdp_r

class hcdp_rm(hcdp_r):
    def __init__(self, num_runs = 3, num_evals = 1000, num_patterns_sol = 10, filename_ini = ""):
        super().__init__(num_runs, num_evals, num_patterns_sol, filename_ini)

    def determine(self, v, fv, s, fs):
        return (v, fv) if fv >= fs else (s, fs)

def usage():
    lib.usage("")

if __name__ == "__main__":
    if ac() == 2 and ss(1) == "-h": usage()
    elif ac() == 1: search = hcdp_rm()
    elif ac() == 5: search = hcdp_rm(si(1), si(2), si(3), ss(4))
    else: usage()
    lib.run(search, lib.print_solution)
