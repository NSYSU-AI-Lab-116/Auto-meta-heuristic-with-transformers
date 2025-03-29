#!/usr/bin/env python
import numpy as np; import time; import sys; import os; import functions
from lib import *

class de:
    def __init__(self, num_runs = 3, num_evals = 1000, num_dims = 2, filename_ini = "", filename_ins = "mvfAckley", pop_size = 10, F = 0.7, cr = 0.5, v_min = -32.0, v_max = 32.0):
        self.num_runs = num_runs
        self.num_evals = num_evals
        self.num_dims = num_dims
        self.filename_ini = filename_ini
        self.filename_ins = filename_ins
        self.pop_size = pop_size
        self.F = F
        self.cr = cr
        self.v_min = v_min
        self.v_max = v_max
        self.seed = int(time.time())
        np.random.seed(self.seed)

    def run(self):
        avg_obj_val = 0.0
        avg_obj_val_eval = np.zeros(self.num_evals)
        for r in range(self.num_runs):
            eval_count = 0
            # 0. initialization
            curr_pop, curr_obj_vals = self.init()
            while eval_count < self.num_evals:
                # 1. mutation
                curr_pop_v = self.mutate(curr_pop)
                # 2. recombination
                curr_pop_u = self.recombine(curr_pop, curr_pop_v)
                # 3. evaluation
                curr_obj_vals_u = self.evaluate(curr_pop_u)
                # 4. selection
                curr_pop = self.select(curr_pop, curr_pop_u, curr_obj_vals, curr_obj_vals_u)
                for i in range(self.pop_size):
                    if self.best_obj_val > curr_obj_vals[i]:
                        self.best_obj_val = curr_obj_vals[i]
                        self.best_sol = curr_pop[i]
                    if eval_count < self.num_evals:
                        avg_obj_val_eval[eval_count] += self.best_obj_val
                        eval_count +=1
            avg_obj_val += self.best_obj_val
        # 4. output
        avg_obj_val /= self.num_runs
        for i in range(self.num_evals):
            avg_obj_val_eval[i] /= self.num_runs
            print("%.15f" % avg_obj_val_eval[i])
        # return curr_pop
        return self.best_sol

    def init(self):
        # 1. initialize all best solution and its objective value
        self.best_sol = self.v_max * np.ones(self.num_dims)
        self.best_obj_val = sys.float_info.max
        # 2. initialize the positions and velocities of particles
        if len(self.filename_ini) == 0:
            curr_pop = self.v_min + (self.v_max - self.v_min) * np.random.rand(self.pop_size, self.num_dims)
        else:
            with open(self.filename_ini, "r") as f:
                curr_pop = np.array(f.read().strip().split(), dtype=float).reshape(self.pop_size, self.num_dims)
        # 3. evaluate the initial population
        curr_obj_vals = self.evaluate(curr_pop)
        return curr_pop, curr_obj_vals

    def evaluate(self, curr_pop):
        return np.array([functions.function_table[self.filename_ins](self.num_dims, x) for x in curr_pop])

    def mutate(self, curr_pop):
        new_pop = np.zeros((self.pop_size, self.num_dims))
        for i in range(self.pop_size):
            s1 = curr_pop[np.random.randint(self.pop_size)]
            s2 = curr_pop[np.random.randint(self.pop_size)]
            s3 = curr_pop[np.random.randint(self.pop_size)]
            new_pop[i] = np.clip(s1 + self.F * (s2 - s3), self.v_min, self.v_max)
        return new_pop

    def recombine(self, curr_pop, curr_pop_v):
        new_pop = np.zeros((self.pop_size, self.num_dims))
        for i in range(self.pop_size):
            s = np.random.randint(self.num_dims)
            for j in range(self.num_dims):
                r = np.random.rand()
                new_pop[i][j] = curr_pop_v[i][j] if (r < self.cr or s == j) else curr_pop[i][j]
        return new_pop

    def select(self, curr_pop, curr_pop_u, curr_obj_vals, curr_obj_vals_u):
        new_pop = np.zeros((self.pop_size, self.num_dims))
        for i in range(self.pop_size):
            if curr_obj_vals_u[i] < curr_obj_vals[i]:
                new_pop[i] = curr_pop_u[i]
                curr_obj_vals[i] = curr_obj_vals_u[i]
            else:
                new_pop[i] = curr_pop[i]
        return new_pop

    def print_parameters(self, algname):
        print("# name of the search algorithm: '%s'" % algname)
        print("# number of runs: %s" % self.num_runs)
        print("# number of evaluations: %s" % self.num_evals)
        print("# number of dimensions: %s" % self.num_dims)
        print("# filename of the initial seeds: '%s'" % self.filename_ini)
        print("# filename of the benchmark: '%s'" % self.filename_ins)
        print("# population size: %s" % self.pop_size)
        print("# F: %s" % self.F)
        print("# crossover rate: %s" % self.cr)
        print("# v_min: %s" % self.v_min)
        print("# v_max: %s" % self.v_max)
        print("# seed: %s" % self.seed)

def usage():
    lib.usage("<#runs> <#evals> <#dims> <filename_ini> <filename_ins> <pop_size> <F> <cr> <v_min> <v_max>", common_params = "")

if __name__ == "__main__":
    if ac() == 2 and ss(1) == "-h": usage()
    elif ac() == 1: search = de()
    elif ac() == 11: search = de(si(1), si(2), si(3), ss(4), ss(5), si(6), sf(7), sf(8), sf(9), sf(10))
    else: usage()
    lib.run(search, lib.print_solution)
