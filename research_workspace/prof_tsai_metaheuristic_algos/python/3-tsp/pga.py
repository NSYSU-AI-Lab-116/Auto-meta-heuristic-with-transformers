#!/usr/bin/env python
import numpy as np; import time; import sys; import os; import math; import threading
from lib import *

class atomic_int:
    def __init__(self, v):
        self.count = v
        self.lock = threading.Lock()

    def set(self, v):
        with self.lock:
            self.count = v
            return self.count

    def dec(self):
        with self.lock:
            self.count -= 1
            return self.count

class pga:
    def __init__(self, num_runs = 3, num_evals = 120000, num_patterns_sol = 1002, filename_ini = "", filename_ins = "pr1002.tsp", pop_size = 120, crossover_rate = 0.4, mutation_rate = 0.1, num_players = 3, num_threads = 6):
        self.num_runs = num_runs
        self.num_evals = num_evals
        self.num_patterns_sol = num_patterns_sol
        self.filename_ini = filename_ini
        self.filename_ins = filename_ins
        self.pop_size = pop_size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.num_players = num_players
        self.num_threads = num_threads
        self.seed = int(time.time())
        np.random.seed(self.seed)

    def run(self):
        self.avg_obj_val = 0.0
        self.avg_obj_val_eval = np.zeros(self.num_evals)
        cv = threading.Condition()
        icnt = atomic_int(self.num_threads)
        for r in range(self.num_runs):
            curr_pop, curr_obj_vals = self.init()
            tmp_curr_pop = curr_pop
            threads = []
            for i in range(self.num_threads):
                thread = threading.Thread(name = "Thread-" + str(i),
                                          target = self.thread_run,
                                          args = (curr_pop,             # r/w (s_idx - e_idx)
                                                  tmp_curr_pop,         # r/w (s_idx - e_idx)
                                                  curr_obj_vals,        # r/w (s_idx - e_idx)
                                                  i, # thread_idx,      # r/o
                                                  self.num_threads,     # r/o
                                                  self.num_evals,       # r/o
                                                  self.pop_size // self.num_threads,    # r/o
                                                  self.crossover_rate,  # r/o
                                                  self.mutation_rate,   # r/o
                                                  self.num_players,     # r/o
                                                  cv,                   # r/w
                                                  icnt                  # r/w
                                                  )
                                          )
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()
        # 4. output
        self.avg_obj_val /= self.num_runs
        for i in range(self.num_evals):
            self.avg_obj_val_eval[i] /= self.num_runs
            print("%.3f" % self.avg_obj_val_eval[i])
        self.show_optimum()
        return curr_pop

    def init(self):
        # 1. initialization
        self.best_sol = np.zeros(self.num_patterns_sol, dtype=int)
        self.best_obj_val = sys.float_info.max
        # 2. input the TSP benchmark
        with open(self.filename_ins, "r") as f:
            self.ins_tsp = np.array(f.read().strip().split(), dtype=float).reshape(self.num_patterns_sol, 2)
        # 3. input the optimal solution
        with open(self.filename_ins + ".opt", "r") as f:
            self.opt_sol = np.array(f.read().strip().split(), dtype=int) - 1
        # 4. initial solutions
        if len(self.filename_ini) > 0:
            with open(self.filename_ini, "r") as f:
                curr_pop = np.array(f.read().strip().split(), dtype=int).reshape(self.pop_size, self.num_patterns_sol)
        else:
            curr_pop = np.array([np.arange(self.num_patterns_sol) for i in range(self.pop_size)])
            for i in range(self.pop_size):
                np.random.shuffle(curr_pop[i])
        # 5. construct the distance matrix
        self.dist = np.zeros((self.num_patterns_sol, self.num_patterns_sol))
        for i in range(self.num_patterns_sol):
            for j in range(self.num_patterns_sol):
                self.dist[i][j] = math.dist(self.ins_tsp[i], self.ins_tsp[j])
        return curr_pop, np.zeros(self.pop_size)

    def thread_run(self,
                   curr_pop,
                   tmp_curr_pop,
                   curr_obj_vals,
                   thread_idx,
                   num_threads,
                   num_evals,
                   thread_pop_size,
                   crossover_rate,
                   mutation_rate,
                   num_players,
                   cv,
                   icnt
                   ):
        # 0. declaration
        num_gens = num_evals // self.pop_size
        s_idx = thread_idx * thread_pop_size
        e_idx = s_idx + thread_pop_size
        gen_count = 0
        while gen_count < num_gens:
            # 1. evaluation
            for i in range(s_idx, e_idx):
                curr_obj_vals[i] = self.evaluate(curr_pop[i])
            cv.acquire()
            if icnt.dec() > 0:
                cv.wait()
            else:
                # 1.1. sync
                z = 0
                avg = self.avg_obj_val_eval[gen_count * self.pop_size : ]      # a slice
                for i in range(self.pop_size):
                    if curr_obj_vals[i] < self.best_obj_val:
                        self.best_obj_val = curr_obj_vals[i]
                        z = i
                    avg[i] += self.best_obj_val
                self.best_sol = curr_pop[z]
                # 1.2. continue
                icnt.set(num_threads)
                cv.notify_all()
            cv.release()
            # 2. determination
            self.tournament_select(curr_pop, curr_obj_vals, tmp_curr_pop, num_players, thread_idx, thread_pop_size)
            cv.acquire()
            if icnt.dec() > 0:
                cv.wait()
            else:
                # 2.1. sync
                curr_pop = tmp_curr_pop
                # 2.2. continue
                icnt.set(num_threads)
                cv.notify_all()
            cv.release()
            # 3. transition
            self.crossover_ox(curr_pop, tmp_curr_pop, crossover_rate, thread_idx, thread_pop_size)
            self.mutate(curr_pop, mutation_rate, thread_idx, thread_pop_size)
            gen_count += 1
        self.avg_obj_val += self.best_obj_val

    def evaluate(self, sol):
        tour_dist = 0.0
        for i in range(self.num_patterns_sol):
            r = sol[i]
            s = sol[(i+1) % self.num_patterns_sol]
            tour_dist += self.dist[r][s]
        return tour_dist

    def tournament_select(self, curr_pop, curr_obj_vals, tmp_curr_pop, num_players, thread_idx, thread_pop_size):
        s_idx = thread_idx * thread_pop_size
        e_idx = s_idx + thread_pop_size
        for i in range(s_idx, e_idx):
            k = np.random.randint(self.pop_size)
            f = curr_obj_vals[k]
            for j in range(1, num_players):
                n = np.random.randint(self.pop_size)
                if curr_obj_vals[n] < f:
                    k = n
                    f = curr_obj_vals[k]
            tmp_curr_pop[i] = curr_pop[k]

    def crossover_ox(self, curr_pop, tmp_curr_pop, cr, thread_idx, thread_pop_size):
        mid = thread_pop_size // 2
        s_idx = thread_idx * thread_pop_size
        m_idx = s_idx + mid
        e_idx = s_idx + thread_pop_size
        ssz = self.num_patterns_sol
        for i in range(s_idx, m_idx):
            f = np.random.rand()
            if f <= cr:
                # 1. create the mapping sections
                xp1 = np.random.randint(ssz + 1)
                xp2 = np.random.randint(ssz + 1)
                if xp1 > xp2:
                    xp1, xp2 = xp2, xp1
                # 2. indices to the two parents and offspring
                p = [ i, i+mid ]
                # 3. the main process of ox
                for k in range(2):
                    c1 = p[k]
                    c2 = p[1-k]
                    # 4. mask the genes between xp1 and xp2
                    s1 = curr_pop[c1]
                    s2 = curr_pop[c2]
                    msk1 = np.zeros(ssz, dtype=bool)
                    for j in range(xp1, xp2):
                        msk1[s1[j]] = True
                    msk2 = np.zeros(ssz, dtype=bool)
                    for j in range(0, ssz):
                        msk2[j] = msk1[s2[j]]
                    # 5. replace the genes that are not masked
                    j = xp2 % ssz
                    for z in range(ssz):
                        if not msk2[z]:
                            tmp_curr_pop[c1][j] = s2[z]
                            j = (j+1) % ssz
        for i in range(s_idx, e_idx):
            curr_pop[i] = tmp_curr_pop[i]

    def mutate(self, curr_pop, mr, thread_idx, thread_pop_size):
        s_idx = thread_idx * thread_pop_size
        e_idx = s_idx + thread_pop_size
        for i in range(s_idx, e_idx):
            f = np.random.rand()
            if f <= mr:
                m1 = np.random.randint(self.num_patterns_sol)   # mutation point
                m2 = np.random.randint(self.num_patterns_sol)   # mutation point
                curr_pop[i][m1], curr_pop[i][m2] = curr_pop[i][m2], curr_pop[i][m1]

    def show_optimum(self):
        opt_dist = 0.0
        for i in range(self.num_patterns_sol):
            r = self.opt_sol[i]
            s = self.opt_sol[(i+1) % self.num_patterns_sol]
            opt_dist += self.dist[r][s]
        lib.print_solution(self.best_sol, prefix = "# Current route: ")
        lib.printf("# Optimum distance: %.3f", opt_dist)
        lib.print_solution(self.opt_sol, prefix = "# Optimum route: ")

    def print_parameters(self, algname):
        print("# name of the search algorithm: '%s'" % algname)
        print("# number of runs: %s" % self.num_runs)
        print("# number of evaluations: %s" % self.num_evals)
        print("# number of patterns (subsolutions) each solution: %s" % self.num_patterns_sol)
        print("# filename of the initial seeds: '%s'" % self.filename_ini)
        print("# filename of the benchmark: '%s'" % self.filename_ins)
        print("# population size: %s" % self.pop_size)
        print("# crossover rate: %s" % self.crossover_rate)
        print("# mutation rate: %s" % self.mutation_rate)
        print("# number of players: %s" % self.num_players)
        print("# number of threads: %s" % self.num_threads)
        print("# seed: %s" % self.seed)

def usage():
    lib.usage("<filename_ins> <pop_size> <cr> <mr> <#players> <#threads>")

if __name__ == "__main__":
    if ac() == 2 and ss(1) == "-h": usage()
    elif ac() == 1: search = pga()
    elif ac() == 11: search = pga(si(1), si(2), si(3), ss(4), ss(5), si(6), sf(7), sf(8), si(9), si(10))
    else: usage()
    lib.run(search, None)
