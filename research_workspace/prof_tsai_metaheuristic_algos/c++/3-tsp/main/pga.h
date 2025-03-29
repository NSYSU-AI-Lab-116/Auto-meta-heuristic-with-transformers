#ifndef __PGA_H_INCLUDED__
#define __PGA_H_INCLUDED__

#include <condition_variable>
#include <thread>
#include <chrono>
#include <atomic>

#include <string>
#include <fstream>
#include <limits>
#include "lib.h"

using namespace std;



class pga
{
public:

    typedef vector<int> solution;
    typedef vector<solution> population;
    typedef vector<double> pattern;
    typedef vector<pattern> instance;
    typedef vector<double> dist_1d;
    typedef vector<dist_1d> dist_2d;

    pga(int num_runs,
        int num_evals,
        int num_patterns_sol,
        string filename_ini,
        string filename_ins,
        int pop_size,
        double crossover_rate,
        double mutation_rate,
        int num_players,
        int num_threads);

    population run();

    static void thread_run(population& curr_pop,
                           population& tmp_curr_pop,
                           vector<double>& curr_obj_vals,
                           const dist_2d& dist,
                           int thread_idx,
                           int num_threads,
                           int nevals,
                           double& best_obj_val,
                           solution& best_sol,
                           pattern& avg_obj_val_eval,
                           int thread_pop_size,
                           double crossover_rate,
                           double mutation_rate,
                           int num_players,
                           std::mutex& cv_m,
                           std::condition_variable& cv,
                           std::atomic<int>& icnt
                           );

private:
    population init();
    static double evaluate(const solution& curr_sol, const dist_2d& dist);
    static void tournament_select(const population& curr_pop, const vector<double>& curr_obj_vals, population& tmp_curr_pop, int num_players, int thread_idx, int thread_pop_size);
    static void crossover_ox(population& curr_pop, population& tmp_curr_pop, double cr, int thread_idx, int thread_pop_size);
    static void mutate(population& curr_pop, double mr, int thread_idx, int thread_pop_size);

private:
    const int num_runs;
    const int num_evals;
    const int num_patterns_sol;
    const string filename_ini;
    const string filename_ins;
    const int pop_size;
    const double crossover_rate;
    const double mutation_rate;
    const int num_players;

    population curr_pop;
    vector<double> curr_obj_vals;
    solution best_sol;
    double best_obj_val;

    instance ins_tsp;
    solution opt_sol;
    dist_2d dist;

    const int num_threads;
};

inline pga::pga(int num_runs,
                int num_evals,
                int num_patterns_sol,
                string filename_ini,
                string filename_ins,
                int pop_size,
                double crossover_rate,
                double mutation_rate,
                int num_players,
                int num_threads
                )
    : num_runs(num_runs),
      num_evals(num_evals),
      num_patterns_sol(num_patterns_sol),
      filename_ini(filename_ini),
      filename_ins(filename_ins),
      pop_size(pop_size),
      crossover_rate(crossover_rate),
      mutation_rate(mutation_rate),
      num_players(num_players),
      num_threads(num_threads)
{
    srand();
}

inline pga::population pga::run()
{
    vector<double> avg_obj_val_eval(num_evals, 0.0);
    std::mutex cv_m;
    std::condition_variable cv;
    std::atomic<int> icnt{num_threads};

    for (int r = 0; r < num_runs; r++) {
        // 0. initialization
        population tmp_curr_pop = curr_pop = init();

        vector<thread> t;
        for (int i = 0; i < num_threads; i++) {
            t.push_back(thread(thread_run,
                               ref(curr_pop),
                               ref(tmp_curr_pop),
                               ref(curr_obj_vals),
                               ref(dist),
                               i, // thread_idx
                               num_threads,
                               num_evals,
                               ref(best_obj_val),
                               ref(best_sol),
                               ref(avg_obj_val_eval),
                               curr_pop.size()/num_threads,
                               crossover_rate,
                               mutation_rate,
                               num_players,
                               ref(cv_m),
                               ref(cv),
                               ref(icnt)
                               ));

            cpu_set_t cpuset;
            CPU_ZERO(&cpuset);
            CPU_SET(i, &cpuset);
            int rc = pthread_setaffinity_np(t[i].native_handle(), sizeof(cpu_set_t), &cpuset);
            if (rc != 0) {
                std::cerr << "Error calling pthread_setaffinity_np: " << rc << "\n";
            }
        }

        for (int i = 0; i < num_threads; i++)
            t[i].join();
    }

    for (int i = 0; i < num_evals; i++) {
        avg_obj_val_eval[i] /= num_runs;
        cout << fixed << setprecision(3) << avg_obj_val_eval[i] << endl;
    }

    cout << best_sol << endl;

    return curr_pop;
}

inline pga::population pga::init()
{
    // 1. parameters initialization
    population curr_pop(pop_size, solution(num_patterns_sol));
    curr_obj_vals.assign(pop_size, 0.0);
    best_obj_val = numeric_limits<double>::max();
    ins_tsp = instance(num_patterns_sol, pattern(2));
    opt_sol = solution(num_patterns_sol);
    dist = dist_2d(num_patterns_sol, dist_1d(num_patterns_sol));

    // 2. input the TSP benchmark
    if (!filename_ins.empty()) {
        ifstream ifs(filename_ins.c_str());
        for (int i = 0; i < num_patterns_sol ; i++)
            for (int j = 0; j < 2; j++)
                ifs >> ins_tsp[i][j];
    }

    // 3. input the optimum solution
    string filename_ins_opt(filename_ins + ".opt");
    if (!filename_ins_opt.empty()) {
        ifstream ifs(filename_ins_opt.c_str());
        for (int i = 0; i < num_patterns_sol ; i++) {
            ifs >> opt_sol[i];
            opt_sol[i]--;
        }
    }


    // 4. initial solutions
    if (!filename_ini.empty()) {
        ifstream ifs(filename_ini.c_str());
        for (int p = 0; p < pop_size; p++)
            for (int i = 0; i < num_patterns_sol; i++)
                ifs >> curr_pop[p][i];
    }
    else {
        for (int p = 0; p < pop_size; p++) {
            for (int i = 0; i < num_patterns_sol; i++)
                curr_pop[p][i] = i;
            for (int i = num_patterns_sol-1; i > 0; --i) // shuffle the solutions
                swap(curr_pop[p][i], curr_pop[p][rand() % (i+1)]);
        }
    }

    // 5. construct the distance matrix
    for (int i = 0; i < num_patterns_sol; i++)
        for (int j = 0; j < num_patterns_sol; j++)
            dist[i][j] = i == j ? 0.0 : distance(ins_tsp[i], ins_tsp[j]);

    return curr_pop;
}

inline void pga::thread_run(population& curr_pop,
                            population& tmp_curr_pop,
                            vector<double>& curr_obj_vals,
                            const dist_2d& dist,
                            int thread_idx,
                            int num_threads,
                            int num_evals,
                            double& best_obj_val,
                            solution& best_sol,
                            pattern& avg_obj_val_eval,
                            int thread_pop_size,
                            double crossover_rate,
                            double mutation_rate,
                            int num_players,
                            std::mutex& cv_m,
                            std::condition_variable& cv,
                            std::atomic<int>& icnt
                            )
{
    // 0. declaration
    const int num_gens = num_evals / curr_pop.size();
    const int s_idx = thread_idx * thread_pop_size;
    const int e_idx = s_idx + thread_pop_size;

    int gen_count = 0;

    while (gen_count < num_gens) {
        // 1. evaluation
        for (int i = s_idx; i < e_idx; i++)
            curr_obj_vals[i] = evaluate(curr_pop[i], dist);
        {
            std::unique_lock<std::mutex> lk(cv_m);
            if (--icnt)
                cv.wait(lk);
            else {
                // 1.1. sync
                size_t z = 0;
                auto avg = &avg_obj_val_eval[gen_count * curr_pop.size()];
                for (size_t i = 0; i < curr_pop.size(); i++) {
                    if (curr_obj_vals[i] < best_obj_val)
                        best_obj_val = curr_obj_vals[z = i];
                    avg[i] += best_obj_val;
                }
                best_sol = curr_pop[z];
                // 1.2. continue
                icnt = num_threads;
                cv.notify_all();
            }
        }

        // 2. determination
        tournament_select(curr_pop, curr_obj_vals, tmp_curr_pop, num_players, thread_idx, thread_pop_size);
        {
            std::unique_lock<std::mutex> lk(cv_m);
            if (--icnt)
                cv.wait(lk);
            else {
                // 2.1. sync
                curr_pop = tmp_curr_pop;
                // 2.2. continue
                icnt = num_threads;
                cv.notify_all();
            }
        }

        // 3. transition
        crossover_ox(curr_pop, tmp_curr_pop, crossover_rate, thread_idx, thread_pop_size);
        mutate(curr_pop, mutation_rate, thread_idx, thread_pop_size);

        ++gen_count;
    }

    // avg_obj_val += best_obj_val;
}

inline double pga::evaluate(const solution& curr_sol, const dist_2d& dist)
{
    double tour_dist = 0.0;
    for (size_t i = 0; i < curr_sol.size(); i++) {
        const int r = curr_sol[i];
        const int s = curr_sol[(i+1) % curr_sol.size()];
        tour_dist += dist[r][s];
    }

    return tour_dist;
}

inline void pga::tournament_select(const population& curr_pop, const vector<double>& curr_obj_vals, population& tmp_curr_pop, int num_players, int thread_idx, int thread_pop_size)
{
    int s_idx = thread_idx * thread_pop_size;
    int e_idx = s_idx + thread_pop_size;

    for (int i = s_idx; i < e_idx; i++) {
        int k = rand() % curr_pop.size();
        double f = curr_obj_vals[k];
        for (int j = 1; j < num_players; j++) {
            int n = rand() % curr_pop.size();
            if (curr_obj_vals[n] < f) {
                k = n;
                f = curr_obj_vals[k];
            }

        }
        tmp_curr_pop[i] = curr_pop[k];
    }
}

inline void pga::crossover_ox(population& curr_pop, population& tmp_curr_pop, double cr, int thread_idx, int thread_pop_size)
{
    const int mid = thread_pop_size / 2;
    const int s_idx = thread_idx * thread_pop_size;
    const int m_idx = thread_idx * thread_pop_size + mid;
    const int e_idx = thread_idx * thread_pop_size + thread_pop_size;
    const size_t ssz = curr_pop[0].size();
    for (int i = s_idx; i < m_idx; i++) {
        const double f = static_cast<double>(rand()) / RAND_MAX;
        if (f <= cr) {
            // 1. create the mapping sections
            size_t xp1 = rand() % (ssz + 1);
            size_t xp2 = rand() % (ssz + 1);
            if (xp1 > xp2)
                swap(xp1, xp2);

            // 2. indices to the two parents and offspring
            const int p[2] = { i, i+mid };

            // 3. the main process of ox
            for (int k = 0; k < 2; k++) {
                const int c1 = p[k];
                const int c2 = p[1-k];

                // 4. mask the genes between xp1 and xp2
                const auto& s1 = curr_pop[c1];
                const auto& s2 = curr_pop[c2];
                vector<bool> msk1(ssz, false);
                for (size_t j = xp1; j < xp2; j++)
                    msk1[s1[j]] = true;
                vector<bool> msk2(ssz, false);
                for (size_t j = 0; j < ssz; j++)
                    msk2[j] = msk1[s2[j]];

                // 5. replace the genes that are not masked
                for (size_t j = xp2 % ssz, z = 0; z < ssz; z++) {
                    if (!msk2[z]) {
                        tmp_curr_pop[c1][j] = s2[z];
                        j = (j+1) % ssz;
                    }
                }
            }
        }
    }
    for (int i = s_idx; i < e_idx; i++)
        curr_pop[i] = tmp_curr_pop[i];
}

inline void pga::mutate(population& curr_pop, double mr, int thread_idx, int thread_pop_size)
{
    const int s_idx = thread_idx * thread_pop_size;
    const int e_idx = thread_idx * thread_pop_size + thread_pop_size;
    for (int i = s_idx; i < e_idx; i++){
        const double f = static_cast<double>(rand()) / RAND_MAX;
        if (f <= mr) {
            int m1 = rand() % curr_pop[0].size();       // mutation point
            int m2 = rand() % curr_pop[0].size();       // mutation point
            swap(curr_pop[i][m1], curr_pop[i][m2]);
        }
    }
}

#endif
