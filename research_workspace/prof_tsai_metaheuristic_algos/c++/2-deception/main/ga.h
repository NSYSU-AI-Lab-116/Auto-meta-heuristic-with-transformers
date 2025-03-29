#ifndef __GA_H_INCLUDED__
#define __GA_H_INCLUDED__

#include <string>
#include <fstream>
#include <numeric>
#include "lib.h"

using namespace std;

class ga
{
public:
    typedef vector<int> solution;
    typedef vector<solution> population;
    typedef vector<int> obj_val_type;

    ga(int num_runs,
       int num_evals,
       int num_patterns_sol,
       string filename_ini,
       int pop_size,
       double crossover_rate,
       double mutation_rate,
       int num_players);

    virtual ~ga() {}

    population run();

private:
    // begin the ga functions
    virtual population select(const population& curr_pop, const obj_val_type& curr_obj_vals, int num_players);
    virtual population crossover(population& curr_pop, double cr);
    population mutate(population& curr_pop, double mr);
    // end the ga functions

private:
    void init();
    virtual obj_val_type evaluate(const population& curr_pop);
    void update_best_sol(const population& curr_pop, const obj_val_type& curr_obj_vals);

private:
    int num_runs;
    int num_evals;
    int num_patterns_sol;
    string filename_ini;

    solution best_sol;
    int best_obj_val;

    // data members for population-based algorithms
    population curr_pop;
    obj_val_type curr_obj_vals;

    // data members for ga-specific parameters
    int pop_size;
    double crossover_rate;
    double mutation_rate;
    int num_players;
};

inline ga::ga(int num_runs,
              int num_evals,
              int num_patterns_sol,
              string filename_ini,
              int pop_size,
              double crossover_rate,
              double mutation_rate,
              int num_players
              )
    : num_runs(num_runs),
      num_evals(num_evals),
      num_patterns_sol(num_patterns_sol),
      filename_ini(filename_ini),
      pop_size(pop_size),
      crossover_rate(crossover_rate),
      mutation_rate(mutation_rate),
      num_players(num_players)
{
    srand();
}

inline ga::population ga::run()
{
    double avg_obj_val = 0;
    vector<double> avg_obj_val_eval(num_evals, 0);

    for (int r = 0; r < num_runs; r++) {
        int eval_count = 0;
        double best_so_far = 0;

        // 0. initialization
        init();

        while (eval_count < num_evals) {
            // 1. evaluation
            curr_obj_vals = evaluate(curr_pop);
            update_best_sol(curr_pop, curr_obj_vals);

            for (int i = 0; i < pop_size; i++) {
                if (best_so_far < curr_obj_vals[i])
                    best_so_far = curr_obj_vals[i];
                if (eval_count < num_evals)
                    avg_obj_val_eval[eval_count++] += best_so_far;
            }

            // 2. determination
            curr_pop = select(curr_pop, curr_obj_vals, num_players);

            // 3. transition
            curr_pop = crossover(curr_pop, crossover_rate);
            curr_pop = mutate(curr_pop, mutation_rate);
        }
        avg_obj_val += best_obj_val;
    }
    avg_obj_val /= num_runs;

    for (int i = 0; i < num_evals; i++) {
        avg_obj_val_eval[i] /= num_runs;
        cout << fixed << setprecision(3) << avg_obj_val_eval[i] << endl;
    }

    return curr_pop;
}

inline void ga::init()
{
    curr_pop = population(pop_size, solution(num_patterns_sol));
    best_obj_val = 0;

    if (!filename_ini.empty()) {
        ifstream ifs(filename_ini.c_str());
        for (int p = 0; p < pop_size; p++)
            for (int i = 0; i < num_patterns_sol; i++)
                ifs >> curr_pop[p][i];
    }
    else {
        for (int p = 0; p < pop_size; p++)
            for (int i = 0; i < num_patterns_sol; i++)
                curr_pop[p][i] = rand() % 2;
    }
}

inline ga::obj_val_type ga::evaluate(const population& curr_pop)
{
    obj_val_type obj_vals(pop_size, 0);
    for (int p = 0; p < pop_size; p++)
        obj_vals[p] = accumulate(curr_pop[p].begin(), curr_pop[p].end(), 0);
    return obj_vals;
}

// tournament selection
inline ga::population ga::select(const population& curr_pop, const obj_val_type& curr_obj_vals, int num_players)
{
    population tmp_pop(curr_pop.size());
    for (size_t i = 0; i < curr_pop.size(); i++) {
        int k = rand() % curr_pop.size();
        double f = curr_obj_vals[k];
        for (int j = 1; j < num_players; j++) {
            int n = rand() % curr_pop.size();
            if (curr_obj_vals[n] > f) {
                k = n;
                f = curr_obj_vals[k];
            }
        }
        tmp_pop[i] = curr_pop[k];
    }
    return tmp_pop;
}

inline void ga::update_best_sol(const population& curr_pop, const obj_val_type& curr_obj_vals)
{
    for (size_t i = 0; i < curr_pop.size(); i++) {
        if (curr_obj_vals[i] > best_obj_val) {
            best_obj_val = curr_obj_vals[i];
            best_sol = curr_pop[i];
        }
    }
}

// one-point crossover
inline ga::population ga::crossover(population& curr_pop, double cr)
{
    const size_t mid = curr_pop.size()/2;
    for (size_t i = 0; i < mid; i++) {
        const double f = static_cast<double>(rand()) / RAND_MAX;
        if (f <= cr) {
            int xp = rand() % curr_pop[0].size();       // crossover point
            for (size_t j = xp; j < curr_pop[0].size(); j++)
                swap(curr_pop[i][j], curr_pop[mid+i][j]);
        }
    }
    return curr_pop;
}

inline ga::population ga::mutate(population& curr_pop, double mr)
{
    for (size_t i = 0; i < curr_pop.size(); i++){
        for (size_t j = 0; j < curr_pop[0].size(); j++){
            const double f = static_cast<double>(rand()) / RAND_MAX;
            if (f <= mr)
                curr_pop[i][j] = !curr_pop[i][j];
        }
    }
    return curr_pop;
}

#endif
