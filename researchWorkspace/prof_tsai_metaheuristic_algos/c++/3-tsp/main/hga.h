#ifndef __HGA_H_INCLUDED__
#define __HGA_H_INCLUDED__

#include <string>
#include <fstream>
#include <limits>
#include "lib.h"
#include "sa.h"

using namespace std;

class hga
{
public:
    typedef vector<int> solution;
    typedef vector<solution> population;
    typedef vector<double> pattern;
    typedef vector<pattern> instance;
    typedef vector<double> dist_1d;
    typedef vector<dist_1d> dist_2d;

    hga(int num_runs,
        int num_evals,
        int num_patterns_sol,
        string filename_ini,
        string filename_ins,
        int pop_size,
        double crossover_rate,
        double mutation_rate,
        int num_players,
        int sa_num_evals,       // parameters of SA
        double sa_time2run,     // parameters of SA
        double max_temp,        // parameters of SA
        double min_temp         // parameters of SA
        );

    population run();

private:
    population init();
    vector<double> evaluate(const population &curr_pop, const dist_2d &dist);
    double evaluate(const solution &curr_sol, const dist_2d &dist);
    void update_best_sol();
    population tournament_select(const population &curr_pop, vector<double> &curr_obj_vals, int num_players);
    population crossover_ox(const population& curr_pop, double cr);
    population mutate(const population& curr_pop, double mr);
    population saf();

private:
    int num_runs;
    int num_evals;
    int num_patterns_sol;
    string filename_ini;
    string filename_ins;

    population curr_pop;
    vector<double> curr_obj_vals;

    solution best_sol;
    double best_obj_val;

    dist_2d dist;
    instance ins_tsp;
    solution opt_sol;

    int pop_size;
    double crossover_rate;
    double mutation_rate;
    int num_players;
    int sa_num_evals;   // parameters of SA
    double sa_time2run; // parameters of SA
    double max_temp;    // parameters of SA
    double min_temp;    // parameters of SA

    int eval_count = 0;
    double best_so_far;
    vector<double> avg_obj_val_eval;
};

inline hga::hga(int num_runs,
                int num_evals,
                int num_patterns_sol,
                string filename_ini,
                string filename_ins,
                int pop_size,
                double crossover_rate,
                double mutation_rate,
                int num_players,
                int sa_num_evals,
                double sa_time2run,
                double max_temp,
                double min_temp
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
      sa_num_evals(sa_num_evals),
      sa_time2run(sa_time2run),
      max_temp(max_temp),
      min_temp(min_temp)
{
    srand();
}

inline hga::population hga::run()
{
    double avg_obj_val = 0;
    avg_obj_val_eval = vector<double>(num_evals, 0.0);

    for (int r = 0; r < num_runs; r++) {
        eval_count = 0;
        best_so_far = numeric_limits<double>::max();

        // 0. initialization
        curr_pop = init();

        while (eval_count < num_evals) {
            // 1. evaluation
            curr_obj_vals = evaluate(curr_pop, dist);
            update_best_sol();

            // 2. determination
            curr_pop = tournament_select(curr_pop, curr_obj_vals, num_players);

            // 3. transition
            curr_pop = crossover_ox(curr_pop, crossover_rate);
            curr_pop = mutate(curr_pop, mutation_rate);

            if (eval_count > num_evals * sa_time2run)
                curr_pop = saf();
        }
        avg_obj_val += best_obj_val;
    }
    avg_obj_val /= num_runs;

    for (int i = 0; i < num_evals; i++) {
        avg_obj_val_eval[i] /= num_runs;
        cout << fixed << setprecision(3) << avg_obj_val_eval[i] << endl;
    }
    cout << best_sol << endl;

    return curr_pop;
}

inline hga::population hga::saf()
{
    population tmp_pop = curr_pop;

    sa sa_search(1,
                 sa_num_evals,
                 curr_pop[0].size(),
                 "",
                 max_temp,
                 min_temp,
                 dist,
                 true);

    int n = 0;
    double v = curr_obj_vals[0];
    for (size_t i = 1; i < curr_pop.size(); i++) {
        if (curr_obj_vals[i] < v) {
            n = i;
            v = curr_obj_vals[i];
        }
    }

    tmp_pop[n] = sa_search.run(curr_pop[n], eval_count, avg_obj_val_eval, best_obj_val, best_sol);

    return tmp_pop;
}

inline hga::population hga::init()
{
    // 1. parameters initialization
    population curr_pop(pop_size, solution(num_patterns_sol));
    ins_tsp = instance(num_patterns_sol, pattern(2, 0.0));
    opt_sol = solution(num_patterns_sol, 0);
    dist = dist_2d(num_patterns_sol, dist_1d(num_patterns_sol, 0.0));
    curr_obj_vals = vector<double>(pop_size, 0.0);
    best_obj_val = numeric_limits<double>::max();

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
            --opt_sol[i];
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
            for (int i = num_patterns_sol-1; i > 0; --i)    // shuffle the solutions
                swap (curr_pop[p][i], curr_pop[p][rand() % (i+1)]);
        }
    }

    // 5. construct the distance matrix
    for (int i = 0; i < num_patterns_sol; i++)
        for (int j = 0; j < num_patterns_sol; j++)
            dist[i][j] = i == j ? 0.0 : distance(ins_tsp[i], ins_tsp[j]);

    return curr_pop;
}

inline vector<double> hga::evaluate(const population &curr_pop, const dist_2d &dist)
{
    vector<double> tour_dist(curr_pop.size(), 0.0);
    for (size_t p = 0; p < curr_pop.size(); p++)
        tour_dist[p] = evaluate(curr_pop[p], dist);
    return tour_dist;
}

inline double hga::evaluate(const solution& curr_sol, const dist_2d &dist)
{
    double tour_dist = 0.0;
    for (size_t i = 0; i < curr_sol.size(); i++) {
        const int r = curr_sol[i];
        const int s = curr_sol[(i+1) % curr_pop[0].size()];
        tour_dist += dist[r][s];
    }

    if (best_so_far > tour_dist)
        best_so_far = tour_dist;
    if (eval_count < num_evals)
        avg_obj_val_eval[eval_count++] += best_so_far;

    return tour_dist;
}

inline void hga::update_best_sol()
{
    for (size_t i = 0; i < curr_pop.size(); i++) {
        if (curr_obj_vals[i] < best_obj_val) {
            best_sol = curr_pop[i];
            best_obj_val = curr_obj_vals[i];
        }
    }
}

inline hga::population hga::tournament_select(const population &curr_pop, vector<double> &curr_obj_vals, int num_players)
{
    population tmp_pop(curr_pop.size());
    for (size_t i = 0; i < curr_pop.size(); i++) {
        int k = rand() % curr_pop.size();
        double f = curr_obj_vals[k];
        for (int j = 1; j < num_players; j++) {
            int n = rand() % curr_pop.size();
            if (curr_obj_vals[n] < f) {
                k = n;
                f = curr_obj_vals[k];
            }
        }
        tmp_pop[i] = curr_pop[k];
    }
    return tmp_pop;
}

inline hga::population hga::crossover_ox(const population& curr_pop, double cr)
{
    population tmp_pop = curr_pop;

    const int mid = curr_pop.size()/2;
    const size_t ssz = curr_pop[0].size();
    for (int i = 0; i < mid; i++) {
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
                        tmp_pop[c1][j] = s2[z];
                        j = (j+1) % ssz;
                    }
                }
            }
        }
    }

    return tmp_pop;
}

inline hga::population hga::mutate(const population& curr_pop, double mr)
{
    population tmp_pop = curr_pop;
    for (size_t i = 0; i < tmp_pop.size(); i++){
        const double f = static_cast<double>(rand()) / RAND_MAX;
        if (f <= mr) {
            const int m1 = rand() % tmp_pop[0].size();  // mutation point
            const int m2 = rand() % tmp_pop[0].size();  // mutation point
            swap(tmp_pop[i][m1], tmp_pop[i][m2]);
        }
    }
    return tmp_pop;
}

#endif
