#!/usr/bin/env python
import numpy as np; import time; import sys; import os; import math
from lib import *

class prega:
    def __init__(self, num_runs = 3, num_evals = 1000, num_patterns_sol = 150, num_dims = 4, num_clusters = 3, filename_ini = "", filename_ins = "iris.data", pop_size = 20, cr = 0.6, mr = 0.1, num_players = 3, num_detections = 80, reduction_rate = 0.1, pra = 1):
        self.num_runs = num_runs
        self.num_evals = num_evals
        self.num_patterns_sol = num_patterns_sol
        self.num_dims = num_dims
        self.num_clusters = num_clusters
        self.filename_ini = filename_ini
        self.filename_ins = filename_ins
        self.pop_size = pop_size
        self.cr = cr
        self.mr = mr
        self.num_players = num_players
        self.num_detections = num_detections
        self.reduction_rate = reduction_rate
        self.pra = pra != 0 # do redundant analysis if true
        self.seed = int(time.time())
        np.random.seed(self.seed)

    def print_parameters(self, algname):
        print("# name of the search algorithm: '%s'" % algname)
        print("# number of runs: %s" % self.num_runs)
        print("# number of evaluations: %s" % self.num_evals)
        print("# number of patterns: %s" % self.num_patterns_sol)
        print("# number of dimensions each pattern: %s" % self.num_dims)
        print("# number of clusters: %s" % self.num_clusters)
        print("# filename of the initial seeds: '%s'" % self.filename_ini)
        print("# name of the data set to be clustered: '%s'" % self.filename_ins)
        print("# population size: %s" % self.pop_size)
        print("# crossover rate: %s" % self.cr)
        print("# mutation rate: %s" % self.mr)
        print("# number of players: %s" % self.num_players)
        print("# number of detections: %s" % self.num_detections)
        print("# reduction rate: %s" % self.reduction_rate)
        print("# pra?: %s" % self.pra)
        print("# seed: %s" % self.seed)

    def run(self):
        avg_obj_val = 0.0
        avg_obj_val_eval = np.zeros(self.num_evals)
        if self.pra:
            pr_kcounter = np.zeros(self.num_evals)
            num_gens = self.num_evals // self.pop_size
            avg_final_state = np.zeros((self.num_runs, num_gens))
            all_final_state = np.zeros((num_gens,))
        for r in range(self.num_runs):
            eval_count = 0
            best_so_far = sys.float_info.max
            # 0. initialization
            curr_pop = self.init()
            centroid_dist = np.zeros((self.pop_size, self.num_clusters))
            pr_mask = np.zeros((self.pop_size, self.num_patterns_sol), dtype=bool)
            if self.pra:
                pop_conv = np.zeros((num_gens, self.pop_size, self.num_patterns_sol), dtype=int)
                final_state = np.zeros((self.num_runs, self.pop_size, self.num_patterns_sol), dtype=int)
                curr_gen = 0
            while eval_count < self.num_evals:
                # 1. evaluation
                curr_obj_vals, centroids = self.evaluate(curr_pop)
                self.update_best_sol(curr_pop, curr_obj_vals)
                if self.pra:
                    self.redundant_analysis_1(curr_gen, curr_pop, pop_conv)
                    curr_gen += 1
                    for p in range(self.pop_size):
                        for i in range(self.num_patterns_sol):
                            if pr_mask[p][i]:
                                pr_kcounter[p+eval_count] += 1
                for i in range(self.pop_size):
                    if best_so_far > curr_obj_vals[i]:
                        best_so_far = curr_obj_vals[i]
                    if eval_count < self.num_evals:
                        avg_obj_val_eval[eval_count] += best_so_far
                        eval_count += 1
                # 2. determination
                curr_pop, pr_mask = self.tournament_select(curr_pop, curr_obj_vals, self.num_players, pr_mask)
                # 3. transition
                curr_pop = self.crossover(curr_pop, self.cr, pr_mask)
                curr_pop = self.mutate(curr_pop, self.mr, pr_mask)
                curr_pop = self.okm(curr_pop, pr_mask, eval_count, centroids, centroid_dist)
                if eval_count > self.num_detections:
                    pr_mask = self.detection(curr_pop, pr_mask, (eval_count + self.pop_size) / self.pop_size, centroids, centroid_dist, self.reduction_rate)
            avg_obj_val += self.best_obj_val
            if self.pra:
                self.redundant_analysis_2(curr_gen, r, pop_conv, final_state, avg_final_state, all_final_state)
        avg_obj_val /= self.num_runs
        avg_obj_val_eval /= self.num_runs
        for i in range(self.num_evals):
            if self.pra:
                print("%.3f, %.3f" % (avg_obj_val_eval[i], pr_kcounter[i] / (self.num_runs * self.num_patterns_sol)))
            else:
                print("%.3f" % avg_obj_val_eval[i])
        return curr_pop

    def init(self):
        self.best_obj_val = sys.float_info.max
        self.best_sol = None
        # 1. input the dataset to be clustered
        if len(self.filename_ins) > 0:
            with open(self.filename_ins, "r") as f:
                self.ins_clustering = np.array(f.read().strip().split(), dtype=float).reshape(self.num_patterns_sol, self.num_dims)
        # 2. create the initial solutions
        if len(self.filename_ini) > 0:
            with open(self.filename_ini, "r") as f:
                curr_pop = np.array(f.read().strip().split(), dtype=float).reshape(self.pop_size, self.num_patterns_sol)
        else:
            curr_pop = np.array([np.array([np.random.randint(self.num_clusters) for _ in range(self.num_patterns_sol)]) for _ in range(self.pop_size)])
        return curr_pop

    def evaluate(self, curr_pop):
        pop_size = len(curr_pop)
        centroids = np.zeros((self.pop_size, self.num_clusters, self.num_dims))
        sse = np.zeros(pop_size)
        for p in range(pop_size):
            # 1. assign each pattern to its cluster
            count_patterns = np.zeros(self.num_clusters, dtype=int)
            for i in range(self.num_patterns_sol):
                k = curr_pop[p][i]
                centroids[p][k] += self.ins_clustering[i]
                count_patterns[k] += 1
            # 2. compute the centroids (means)
            for k in range(self.num_clusters):
                centroids[p][k] /= count_patterns[k]
            # 3. compute sse
            for i in range(self.num_patterns_sol):
                k = curr_pop[p][i]
                for d in range(self.num_dims):
                    sse[p] += math.pow(self.ins_clustering[i][d] - centroids[p][k][d], 2)
        return sse, centroids

    # tournament selection
    def tournament_select(self, curr_pop, curr_obj_vals, num_players, pr_mask):
        pop_size = len(curr_pop)
        tmp_pop = np.empty((pop_size, self.num_patterns_sol), dtype=int)
        tmp_pr_mask = np.zeros((pop_size, self.num_patterns_sol), dtype=bool)
        for i in range(pop_size):
            k = np.random.randint(pop_size)
            f = curr_obj_vals[k]
            for _ in range(1, num_players):
                n = np.random.randint(pop_size)
                if curr_obj_vals[n] < f:
                    k = n
                    f = curr_obj_vals[k]
            tmp_pop[i] = curr_pop[k]
            tmp_pr_mask[i] = pr_mask[k]
        return tmp_pop, tmp_pr_mask

    def update_best_sol(self, curr_pop, curr_obj_vals):
        pop_size = len(curr_pop)
        for i in range(pop_size):
            if curr_obj_vals[i] < self.best_obj_val:
                self.best_obj_val = curr_obj_vals[i]
                self.best_sol = curr_pop[i]

    # one-point crossover
    def crossover(self, curr_pop, cr, pr_mask):
        pop_size = len(curr_pop)
        mid = pop_size // 2
        for i in range(mid):
            f = np.random.rand()
            if f <= cr:
                xp = np.random.randint(self.num_patterns_sol)   # crossover point
                for j in range(xp, self.num_patterns_sol):
                    if not pr_mask[i][j]:
                        curr_pop[i][j], curr_pop[mid+i][j] = curr_pop[mid+i][j], curr_pop[i][j]
        return curr_pop

    def mutate(self, curr_pop, mr, pr_mask):
        pop_size = len(curr_pop)
        for i in range(pop_size):
            f = np.random.rand()
            if f <= mr:
                m = np.random.randint(self.num_patterns_sol)    # mutation point
                if not pr_mask[i][m]:
                    curr_pop[i][m] = np.random.randint(self.num_clusters)
        return curr_pop

    # one-evaluation k-means
    def okm(self, curr_pop, pr_mask, eval, centroids, centroid_dist):
        pop_size = len(curr_pop)
        for p in range(pop_size):
            # 1. one iteration k-means
            count = np.zeros(self.num_clusters, dtype=int)
            for i in range(self.num_patterns_sol):
                if not pr_mask[p][i] or eval > self.num_evals/2:
                    dist = sys.float_info.max
                    c = 0
                    for k in range(self.num_clusters):
                        dist_tmp = math.dist(self.ins_clustering[i], centroids[p][k])
                        if dist_tmp < dist:
                            dist = dist_tmp
                            c = k
                    curr_pop[p][i] = c
                    count[c] += 1
                    if centroid_dist[p][c] < dist:
                        centroid_dist[p][c] = dist
            # 2. randomly assign a pattern to each empty cluster
            for k in range(self.num_clusters):
                if count[k] == 0:
                    i = np.random.randint(self.num_patterns_sol)
                    curr_pop[p][i] = k
                    if pr_mask[p][i]:
                        pr_mask[p][i] = False
        return curr_pop

    def detection(self, curr_pop, pr_mask, eval, centroids, centroid_dist, reduction_rate):
        rr = eval * reduction_rate
        for p in range(self.pop_size):
            dist = np.empty(self.num_clusters, dtype=float)
            for i in range(self.num_clusters):
                dist[i] = centroid_dist[p][i] * rr
            for i in range(self.num_patterns_sol):
                if not pr_mask[p][i]:
                    dist_tmp = math.dist(self.ins_clustering[i], centroids[p][curr_pop[p][i]])
                    if dist_tmp < dist[curr_pop[p][i]]:
                        pr_mask[p][i] = True
        return pr_mask

    def redundant_analysis_1(self, curr_gen, curr_pop, pop_conv):
        pop_conv[curr_gen] = curr_pop

    def redundant_analysis_2(self, curr_gen, curr_run, pop_conv, final_state, avg_final_state, all_final_state):
        # 1. find the generation at which each subsolution reaches the final state for each run
        for i in range(self.pop_size):
            for j in range(self.num_patterns_sol):
                for k in range(curr_gen-1, 1, -1):
                    if pop_conv[k][i][j] != pop_conv[k-1][i][j]:
                        final_state[curr_run][i][j] = k
                        break
        # 2. accumulate the information obtained above for each run
        for k in range(curr_gen):
            final_state_count = 0
            for i in range(self.pop_size):
                for j in range(self.num_patterns_sol):
                    if final_state[curr_run][i][j] <= k:
                        final_state_count += 1
            avg_final_state[curr_run][k] = final_state_count / self.pop_size
            all_final_state[k] += avg_final_state[curr_run][k]
        # 3. compute the percentage of subsolutions that reach the final state for all runs
        if curr_run == self.num_runs-1:
            print("# rd: ", end='')
            for k in range(curr_gen):
                print(("%.3f" if k == 0 else ", %.3f") % (all_final_state[k] / (self.num_runs * self.num_patterns_sol)), end='')
            print()

def usage():
    lib.usage("<#runs> <#evals> <#patterns> <#dims> <#clusters> <filename_ini> <filename_ins> <pop_size> <cr> <mr> <#players> <#detections> <rr> <pra?>", common_params = "")

if __name__ == "__main__":
    if ac() == 2 and ss(1) == "-h": usage()
    if ac() == 1: search = prega()
    elif ac() == 15: search = prega(si(1), si(2), si(3), si(4), si(5), ss(6), ss(7), si(8), sf(9), sf(10), si(11), si(12), sf(13), si(14))
    else: usage()
    lib.run(search, lib.print_population)
