#ifndef __GA_H_INCLUDED__
#define __GA_H_INCLUDED__

#include <string>
#include <fstream>
#include <limits>
#include "lib.h"

using namespace std;

class ga
{
public:

    typedef vector<int> solution;
    typedef vector<solution> population;
    typedef vector<double> pattern;
    typedef vector<pattern> instance;
    typedef vector<double> dist_1d;
    typedef vector<dist_1d> dist_2d;

    ga(int num_runs,
       int num_evals,
       int num_patterns_sol,
       string filename_ini,
       string filename_ins,
       int pop_size,
       double crossover_rate,
       double mutation_rate,
       int num_players);

    population run();

private:
    population init();
    vector<double> evaluate(const population &curr_pop, const dist_2d &dist);
    void update_best_sol(const population &curr_pop, const vector<double> &curr_obj_vals, solution &best_sol, double &best_obj_val);
    population tournament_select(const population &curr_pop, vector<double> &curr_obj_vals, int num_players);
    virtual population crossover(const population& curr_pop, double cr);
    population mutate(const population& curr_pop, double mr);

private:
    const int num_runs;
    const int num_evals;
    const int num_patterns_sol;
    const string filename_ini;
    const string filename_ins;
    const int pop_size;
    const double crossover_rate;
    const double mutation_rate;
    int num_players;

    population curr_pop;
    vector<double> curr_obj_vals;
    solution best_sol;
    double best_obj_val;

    instance ins_tsp;
    solution opt_sol;
    dist_2d dist;
};

inline ga::ga(int num_runs,
              int num_evals,
              int num_patterns_sol,
              string filename_ini,
              string filename_ins,
              int pop_size,
              double crossover_rate,
              double mutation_rate,
              int num_players
              )
    : num_runs(num_runs),
      num_evals(num_evals),
      num_patterns_sol(num_patterns_sol),
      filename_ini(filename_ini),
      filename_ins(filename_ins),
      pop_size(pop_size),
      crossover_rate(crossover_rate),
      mutation_rate(mutation_rate),
      num_players(num_players)
{
    srand();
}

inline ga::population ga::run()
{
    // double avg_obj_val = 0;
    vector <double> avg_obj_val_eval(num_evals, 0.0);

    for (int r = 0; r < num_runs; r++) {
        int eval_count = 0;
        double best_so_far = numeric_limits<double>::max();

        // 0. initialization
        curr_pop = init();

        while (eval_count < num_evals) {
            // 1. evaluation
            curr_obj_vals = evaluate(curr_pop, dist);

            update_best_sol(curr_pop, curr_obj_vals, best_sol, best_obj_val); // please check to see if it is redundant

            for (int i = 0; i < pop_size; i++) {
                if (best_so_far > curr_obj_vals[i])
                    best_so_far = curr_obj_vals[i];
                if (eval_count < num_evals)
                    avg_obj_val_eval[eval_count++] += best_so_far;
            }

            // 2. determination
            curr_pop = tournament_select(curr_pop, curr_obj_vals, num_players);

            // 3. transition
            curr_pop = crossover(curr_pop, crossover_rate);
            curr_pop = mutate(curr_pop, mutation_rate);
        }

        // avg_obj_val += best_obj_val;
    }

    // avg_obj_val /= num_runs;

    for (int i = 0; i < num_evals; i++) {
        avg_obj_val_eval[i] /= num_runs;
        cout << fixed << setprecision(3) << avg_obj_val_eval[i] << endl;
    }

    cout << best_sol << endl;

    return curr_pop;
}

inline ga::population ga::init()
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

inline vector<double> ga::evaluate(const population &curr_pop, const dist_2d &dist)
{
    vector<double> tour_dist(curr_pop.size(), 0.0);
    for (size_t p = 0; p < curr_pop.size(); p++) {
        for (size_t i = 0; i < curr_pop[p].size(); i++) {
            const int r = curr_pop[p][i];
            const int s = curr_pop[p][(i+1) % curr_pop[p].size()];
            tour_dist[p] += dist[r][s];
        }
    }
    return tour_dist;
}

inline void ga::update_best_sol(const population &curr_pop, const vector<double> &curr_obj_vals, solution &best_sol, double &best_obj_val)
{
    for (size_t i = 0; i < curr_pop.size(); i++) {
        if (curr_obj_vals[i] < best_obj_val) {
            best_sol = curr_pop[i];
            best_obj_val = curr_obj_vals[i];
        }
    }
}

inline ga::population ga::tournament_select(const population &curr_pop, vector<double> &curr_obj_vals, int num_players)
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

inline ga::population ga::crossover(const population& curr_pop, double cr)
{
    population tmp_pop = curr_pop;

    const size_t mid = tmp_pop.size()/2;
    const size_t ssz = tmp_pop[0].size();
    for (size_t i = 0; i < mid; i++) {
        const double f = static_cast<double>(rand()) / RAND_MAX;
        if (f <= cr) {
            // 1. one-point crossover
            const int xp = rand() % ssz;
            solution& s1 = tmp_pop[i];
            solution& s2 = tmp_pop[mid+i];
            swap_ranges(s1.begin()+xp, s1.end(), s2.begin()+xp);

            // 2. correct the solutions
            for (size_t j = i; j < tmp_pop.size(); j += mid) {
                solution& s = tmp_pop[j];

                // find the number of times each city was visited,
                // which can be either 0, 1, or 2; i.e., not visited,
                // visited once, and visited twice
                vector<int> visit(ssz, 0);
                for (size_t k = 0; k < ssz; k++)
                    ++visit[s[k]];

                // put cities not visited in bag
                vector<int> bag;
                for (size_t k = 0; k < ssz; k++)
                    if (visit[k] == 0)
                        bag.push_back(k);

                // correct cities visited twice, by replacing one of
                // which by one randomly chosen from the bag, if
                // necessary
                if (bag.size() > 0) {
                    random_shuffle(bag.begin(), bag.end());
                    for (size_t n = 0, k = xp; k < ssz; k++) {
                        if (visit[s[k]] == 2)
                            s[k] = bag[n++];
                    }
                }
            }
        }
    }

    return tmp_pop;
}

inline ga::population ga::mutate(const population& curr_pop, double mr)
{
    population tmp_pop = curr_pop;

    for (size_t i = 0; i < tmp_pop.size(); i++){
        const double f = static_cast<double>(rand()) / RAND_MAX;
        if (f <= mr) {
            int m1 = rand() % tmp_pop[0].size();        // mutation point
            int m2 = rand() % tmp_pop[0].size();        // mutation point
            swap(tmp_pop[i][m1], tmp_pop[i][m2]);
        }
    }

    return tmp_pop;
}

#endif
