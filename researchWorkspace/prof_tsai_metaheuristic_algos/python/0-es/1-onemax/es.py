#!/usr/bin/env python
import numpy as np; import time; import sys; import os
from lib import *

class es:
    def __init__(self, num_bits = 10):
        self.num_bits = num_bits

    def run(self):
        max_sol = 2**self.num_bits - 1
        s = 0
        fs = self.evaluate(s)
        print('{0} # {1:0{2}b}'.format(fs, s, self.num_bits))
        v = s
        while v < max_sol:
            v = self.transit(v)
            fv = self.evaluate(v)
            fs, s = self.determine(fv, v, fs, s)
            print('{0} # {1:0{2}b}'.format(fs, v, self.num_bits))

    def transit(self, s):
        s += 1
        return s

    def evaluate(self, s):
        return bin(s).count("1")

    def determine(self, fv, v, fs, s):
        if fv > fs:
            fs, s = fv, v
        return fs, s

    def print_parameters(self, algname):
        print("# name of the search algorithm: '%s'" % algname)
        print("# number of bits: %d" % self.num_bits)

def usage():
    lib.usage("<num_bits>", common_params = "")

if __name__ == "__main__":
    if ac() == 2 and ss(1) == "-h": usage()
    elif ac() == 1: search = es()
    elif ac() == 2: search = es(si(1))
    else: usage()
    lib.run(search, None)
