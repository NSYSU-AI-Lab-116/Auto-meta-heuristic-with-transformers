#!/usr/bin/env python
import numpy as np; import time; import sys; import os; import functions
from lib import *

class pso:
    def __init__(self, num_runs = 3, num_evals = 1000, num_dims = 2, filename_ini = "", filename_ins = "mvfAckley", pop_size = 10, omega = 0.5, c1 = 1.0, c2 = 1.5, v_min = -32.0, v_max = 32.0):
        self.num_runs = num_runs
        self.num_evals = num_evals
        self.num_dims = num_dims
        self.filename_ini = filename_ini
        self.filename_ins = filename_ins
        self.pop_size = pop_size
        self.omega = omega
        self.c1 = c1
        self.c2 = c2
        self.v_min = v_min
        self.v_max = v_max
        self.seed = int(time.time())
        np.random.seed(self.seed)

    def run(self):
        avg_obj_val = 0.0
        avg_obj_val_eval = np.zeros(self.num_evals)
        for r in range(self.num_runs):
            eval_count = 0
            best_so_far = sys.float_info.max
            # 0. initialization
            curr_pop, curr_obj_vals, velocity = self.init()
            while eval_count < self.num_evals:
                # 1. compute new velocity of each particle
                velocity = self.new_velocity(curr_pop, velocity)
                # 2. adjust all the particles to their new positions
                curr_pop = self.new_position(curr_pop, velocity)
                # 3. evaluation
                curr_obj_vals = self.evaluate(curr_pop)
                for i in range(self.pop_size):
                    if best_so_far > curr_obj_vals[i]:
                        best_so_far = curr_obj_vals[i]
                    if eval_count < self.num_evals:
                        avg_obj_val_eval[eval_count] += best_so_far
                        eval_count += 1
                # 4. update
                self.update_pb(curr_pop, curr_obj_vals)
                self.update_gb(curr_pop, curr_obj_vals)
                self.update_best_sol()
            avg_obj_val += self.best_obj_val
        # 4. output
        avg_obj_val /= self.num_runs
        for i in range(self.num_evals):
            avg_obj_val_eval[i] /= self.num_runs
            print("%.15f" % avg_obj_val_eval[i])
        # return curr_pop
        return self.best_sol

    def init(self):
        # 1. initialize all best solutions and their objective values
        self.pbest = sys.float_info.max * np.ones((self.pop_size, self.num_dims))
        self.pbest_obj_vals = sys.float_info.max * np.ones(self.pop_size)
        self.gbest = self.v_max * np.ones(self.num_dims)
        self.gbest_obj_val = sys.float_info.max
        self.best_sol = self.gbest
        self.best_obj_val = self.gbest_obj_val
        # 2. initialize the positions and velocities of particles
        if len(self.filename_ini) == 0:
            curr_pop = self.v_min + (self.v_max - self.v_min) * np.random.rand(self.pop_size, self.num_dims)
        else:
            with open(self.filename_ini, "r") as f:
                curr_pop = np.array(f.read().strip().split(), dtype=float).reshape(self.pop_size, self.num_dims)
        velocity = curr_pop / float(self.num_evals)
        # 3. evaluation
        curr_obj_vals = self.evaluate(curr_pop)
        # 4. update
        self.update_pb(curr_pop, curr_obj_vals)
        self.update_gb(curr_pop, curr_obj_vals)
        self.update_best_sol()
        return curr_pop, curr_obj_vals, velocity

    def evaluate(self, curr_pop):
        return np.array([functions.function_table[self.filename_ins](self.num_dims, x) for x in curr_pop])

    def update_pb(self, curr_pop, curr_obj_vals):
        for i in range(self.pop_size):
            if curr_obj_vals[i] < self.pbest_obj_vals[i]:
                self.pbest_obj_vals[i] = curr_obj_vals[i]
                self.pbest[i] = curr_pop[i]

    def update_gb(self, curr_pop, curr_obj_vals):
        for i in range(self.pop_size):
            if curr_obj_vals[i] < self.gbest_obj_val:
                self.gbest_obj_val = curr_obj_vals[i]
                self.gbest = curr_pop[i]

    def update_best_sol(self):
        if self.gbest_obj_val < self.best_obj_val:
            self.best_obj_val = self.gbest_obj_val
            self.best_sol = self.gbest

    def new_velocity(self, curr_pop, velocity):
        r1 = np.random.rand(self.pop_size, self.num_dims)
        r2 = np.random.rand(self.pop_size, self.num_dims)
        new_v = np.zeros((self.pop_size, self.num_dims)) # FIXME, why this line is needed to make it right?!
        new_v = self.omega * velocity + self.c1 * r1 * (self.pbest - curr_pop) + self.c2 * r2 * (self.gbest - curr_pop)
        return np.clip(new_v, self.v_min, self.v_max)

    def new_position(self, curr_pop, velocity):
        return np.clip(curr_pop + velocity, self.v_min, self.v_max)

    def print_parameters(self, algname):
        print("# name of the search algorithm: '%s'" % algname)
        print("# number of runs: %s" % self.num_runs)
        print("# number of evaluations: %s" % self.num_evals)
        print("# number of dimensions: %s" % self.num_dims)
        print("# filename of the initial seeds: '%s'" % self.filename_ini)
        print("# filename of the benchmark: '%s'" % self.filename_ins)
        print("# population size: %s" % self.pop_size)
        print("# omega: %s" % self.omega)
        print("# c1: %s" % self.c1)
        print("# c2: %s" % self.c2)
        print("# v_min: %s" % self.v_min)
        print("# v_max: %s" % self.v_max)

def usage():
    lib.usage("<#runs> <#evals> <#dims> <filename_ini> <filename_ins> <pop_size> <omega> <c1> <c2> <v_min> <v_max>", common_params = "")

if __name__ == "__main__":
    if ac() == 2 and ss(1) == "-h": usage()
    elif ac() == 1: search = pso()
    elif ac() == 12: search = pso(si(1), si(2), si(3), ss(4), ss(5), si(6), sf(7), sf(8), sf(9), sf(10), sf(11))
    else: usage()
    lib.run(search, lib.print_solution)
