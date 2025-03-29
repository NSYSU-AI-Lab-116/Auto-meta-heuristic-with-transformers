#!/usr/bin/env python
import numpy as np; import time; import sys; import os; import math
from lib import *

class se:
    def __init__(self, num_runs = 3, num_evals = 10000, num_bits_sol = 100, filename_ini = "", num_searchers = 1, num_regions = 1, num_samples = 1, num_players = 1, scatter_plot = 0):
        self.num_runs = num_runs
        self.num_evals = num_evals
        self.num_bits_sol = num_bits_sol
        self.filename_ini = filename_ini
        self.num_searchers = num_searchers
        self.num_regions = num_regions
        self.num_samples = num_samples
        self.num_players = num_players
        self.scatter_plot = scatter_plot != 0
        self.num_id_bits = int(math.log2(num_regions))
        self.id_bits = np.empty((num_regions, self.num_id_bits), dtype=int)
        self.seed = int(time.time())
        np.random.seed(self.seed)

    def run(self):
        avg_obj_val_eval = np.zeros(self.num_evals)
        for r in range(self.num_runs):
            self.eval_count = 0
            self.init()                         # 1. initialization
            self.resource_arrangement()         # 2. resource arrangement
            while self.eval_count < self.num_evals:
                eval_cc = self.eval_count
                self.vision_search(eval_cc)     # 3. vision search
                self.marketing_survey()         # 4. marketing survey
                avg_obj_val_eval[eval_cc:min(self.eval_count, self.num_evals)] += self.best_so_far
        avg_obj_val_eval /= self.num_runs
        for i in range(self.num_evals):
            print("%.3f" % avg_obj_val_eval[i])

    # 1. initialization
    def init(self):
        n_searchers = self.num_searchers
        n_regions = self.num_regions
        n_samples = self.num_samples
        n_bits_sol = self.num_bits_sol
        # set aside arrays for searchers, samples, and sampleV
        self.searcher_sol = np.array([np.array([0 if _ < 0.5 else 1 for _ in np.random.rand(n_bits_sol)], dtype=int) for _ in range(n_searchers)], dtype=int)
        self.sample_sol = np.zeros((n_regions, n_samples, n_bits_sol), dtype=int)
        self.sample_sol_best = np.zeros((n_regions, n_bits_sol), dtype=int)
        self.sampleV_sol = np.zeros((n_searchers, n_regions, 2*n_samples, n_bits_sol), dtype=int)
        self.searcher_sol_fitness = np.zeros(n_searchers, dtype=float)
        self.sample_sol_fitness = np.zeros((n_regions, n_samples), dtype=float)
        self.sample_sol_best_fitness = np.zeros(n_regions, dtype=float)
        self.sampleV_sol_fitness = np.zeros((n_searchers, n_regions, 2*n_samples), dtype=float)
        self.best_sol = np.zeros(n_bits_sol, dtype=int)
        self.best_so_far = 0

    # 2. resource arrangement
    def resource_arrangement(self):
        n_searchers = self.num_searchers
        n_regions = self.num_regions
        n_samples = self.num_samples
        n_bits_sol = self.num_bits_sol
        n_id_bits = self.num_id_bits
        # 2.1. initialize searchers and regions
        ## regions_id_bits()
        self.id_bits = np.array([np.array(list('{0:0{1}b}'.format(j, n_id_bits))) for j in range(n_regions)], dtype=int)
        # 2.1.1 assign searchers to regions
        self.searcher_region_id = np.array([i % n_regions for i in range(n_searchers)], dtype=int)
        ## assign_searcher to region (i, i % num_regions)
        self.searcher_sol[:, :n_id_bits] = np.array([self.id_bits[i % n_regions] for i in range(n_searchers)], dtype=int)
        # 2.1.2 initialize sample solutions
        for j in range(n_regions):
            for k in range(n_samples):
                self.sample_sol[j][k][:n_id_bits] = self.id_bits[j]
                self.sample_sol[j][k][n_id_bits:] = np.array([0 if _ < 0.5 else 1 for _ in np.random.rand(n_bits_sol-n_id_bits)])
        # 2.2. initialize investment and how long regions have not been searched
        self.ta = np.zeros(n_regions)
        self.tb = np.ones(n_regions)
        for i in range(n_searchers):
            j = self.searcher_region_id[i]
            self.ta[j] += 1
            self.tb[j] = 1
        # 2.3. initialize expected values (ev)
        self.expected_value = np.zeros((n_searchers, n_regions))
        self.T_j = np.zeros(n_regions)
        self.M_j = np.zeros(n_regions)

    # 3. vision search
    def vision_search(self, eval):
        # 3.1 construct V (searcher X sample)
        if eval > 0:
            self.transit()
        # 3.2 compute the expected value of all regions of searchers
        self.compute_expected_value(eval)
        # 3.3 select region to which a searcher will be assigned
        self.vision_selection(self.num_players, eval)

    # 3.1 construct V (searcher X sample)
    def transit(self):
        n_searchers = self.num_searchers
        n_regions = self.num_regions
        n_samples = self.num_samples
        n_bits_sol = self.num_bits_sol
        n_id_bits = self.num_id_bits
        # 3.1.1 exchange information between searchers and samples
        for i in range(n_searchers):
            for j in range(n_regions):
                for k in range(n_samples):
                    x = np.random.randint(n_bits_sol + 1)
                    m = k << 1
                    n = m + 1
                    self.sampleV_sol[i][j][m][:n_id_bits] = self.id_bits[j]
                    self.sampleV_sol[i][j][n][:n_id_bits] = self.id_bits[j]
                    self.sampleV_sol[i][j][m][n_id_bits:x] = self.searcher_sol[i][n_id_bits:x]
                    self.sampleV_sol[i][j][n][n_id_bits:x] = self.sample_sol[j][k][n_id_bits:x]
                    self.sampleV_sol[i][j][m][x:n_bits_sol] = self.sample_sol[j][k][x:n_bits_sol]
                    self.sampleV_sol[i][j][n][x:n_bits_sol] = self.searcher_sol[i][x:n_bits_sol]
        # 3.1.2 randomly change one bit of each solution in sampleV_sol
        for i in range(n_searchers):
            for j in range(n_regions):
                for k in range(2*n_samples):
                    m = np.random.randint(n_bits_sol) # bit to mutate
                    if m >= n_id_bits:
                        self.sampleV_sol[i][j][k][m] ^= 1

    # 3.2 expected value for onemax problem
    def compute_expected_value(self, eval):
        n_searchers = self.num_searchers
        n_regions = self.num_regions
        n_samples = self.num_samples
        n_bits_sol = self.num_bits_sol
        # 3.2.1 fitness value of searchers and sampleV_sol (new candidate solutions)
        if eval == 0:
            # 3.2.1a fitness value of searchers
            self.searcher_sol_fitness = np.array([self.evaluate_fitness(self.searcher_sol[i]) for i in range(n_searchers)])
        else:
            # 3.2.1b fitness value of sampleV_sol (new candidate solutions)
            for i in range(n_searchers):
                j = self.searcher_region_id[i]
                if self.scatter_plot == 1:
                    print("%d %.6f %d " % (self.eval_count, j-0.1*i+0.1*n_regions/2, i), end='')
                for k in range(n_samples):
                    n = np.random.randint(2*n_samples)
                    f = self.evaluate_fitness(self.sampleV_sol[i][j][n])
                    if f > self.searcher_sol_fitness[i]:
                        self.searcher_sol[i] = self.sampleV_sol[i][j][n]
                        self.searcher_sol_fitness[i] = f
                    if f > self.sample_sol_fitness[j][k]:
                        self.sample_sol[j][k] = self.sampleV_sol[i][j][n]
                        self.sample_sol_fitness[j][k] = f
            if self.scatter_plot == 1:
                print()
        # 3.2.2 fitness value of samples
        if eval == 0:
            self.sample_sol_fitness = np.array([np.array([self.evaluate_fitness(self.sample_sol[j][k]) for k in range(n_samples)]) for j in range(n_regions)])
        total_sample_fitness = 0.0 # f(m_j)
        for j in range(n_regions):
            rbj = 0.0
            b = -1
            for k in range(n_samples):
                total_sample_fitness += self.sample_sol_fitness[j][k]
                # update fbj
                if self.sample_sol_fitness[j][k] > rbj:
                    b = k
                    rbj = self.sample_sol_fitness[j][k]
            if b >= 0:
                self.sample_sol_best_fitness[j] = rbj
                self.sample_sol_best[j] = self.sample_sol[j][b]
        # 3.2.3 M_j
        self.M_j = self.sample_sol_best_fitness / total_sample_fitness
        # 3.2.4 T_j
        self.T_j = self.ta / self.tb
        # 3.2.5 compute the expected_value
        self.expected_value = np.array([self.T_j * self.M_j for _ in range(n_searchers)])

    # subfunction: 3.2.1 fitness value
    def evaluate_fitness(self, sol):
        self.eval_count += 1
        return sum(sol)

    # 3.3 select region to which a searcher will be assigned
    def vision_selection(self, player, eval):
        n_searchers = self.num_searchers
        n_regions = self.num_regions
        n_samples = self.num_samples
        n_bits_sol = self.num_bits_sol
        n_players = self.num_players
        self.tb += 1
        # find index of the best vij
        for i in range(n_searchers):
            j = np.random.randint(n_regions)
            ev = self.expected_value[i][j]
            for _ in range(n_players - 1):
                c = np.random.randint(n_regions)
                if self.expected_value[i][c] > ev:
                    j = c
                    ev = self.expected_value[i][c]
            # assign searcher i to region j
            self.searcher_region_id[i] = j
            # update ta[j] and tb[j]
            self.ta[j] += 1
            self.tb[j] = 1

    # 4. marketing survey
    def marketing_survey(self):
        for j in range(self.num_regions):
            if self.tb[j] > 1:
                self.ta[j] = 1
        for i in range(self.num_searchers):
            if self.searcher_sol_fitness[i] > self.best_so_far:
                self.best_so_far = self.searcher_sol_fitness[i]
                self.best_sol = self.searcher_sol[i]
        for j in range(self.num_regions):
            for k in range(self.num_samples):
                if self.sample_sol_fitness[j][k] > self.best_so_far:
                    self.best_so_far = self.sample_sol_fitness[j][k]
                    self.best_sol = self.sample_sol[j][k]

    def print_parameters(self, algname):
        print("# name of the search algorithm: '%s'" % algname)
        print("# number of runs: %s" % self.num_runs)
        print("# number of evaluations: %s" % self.num_evals)
        print("# number of patterns: %s" % self.num_bits_sol)
        print("# filename of the initial seeds: '%s'" % self.filename_ini)
        print("# number of searchers: %s" % self.num_searchers)
        print("# number of regions: %s" % self.num_regions)
        print("# number of samples: %s" % self.num_samples)
        print("# number of players: %s" % self.num_players)
        print("# scatter plot?: %s" % self.scatter_plot)
        print("# seed: %s" % self.seed)

def usage():
    lib.usage("<#searchers> <#regions> <#samples> <#players> <scatter_plot?>")

if __name__ == "__main__":
    if ac() == 2 and ss(1) == "-h": usage()
    elif ac() == 1: search = se()
    elif ac() == 10: search = se(si(1), si(2), si(3), ss(4), si(5), si(6), si(7), si(8), si(9))
    else: usage()
    lib.run(search, lib.print_population)
