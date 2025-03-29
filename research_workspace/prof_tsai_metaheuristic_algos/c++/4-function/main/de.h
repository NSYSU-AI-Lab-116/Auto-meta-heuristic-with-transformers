#ifndef __DE_H_INCLUDED__
#define __DE_H_INCLUDED__

#include <iostream>
#include <fstream>
#include <limits>
#include "de.h"
#include "lib.h"
#include "functions.h"

using namespace std;

class de
{
public:
    using solution = vector<double>;
    using population = vector<solution>;

    de(int num_runs,
       int num_evals,
       int num_dims,
       string filename_ini,
       string filename_ins,
       int pop_size,
       double F,
       double cr,
       double vmin,
       double vmax);

    virtual ~de() {}

    population run();

    vector<double> evaluate(string function_name, int dims, const population& curr_pop);
    virtual population mutate(const population& curr_pop, double F, double vmin, double vmax, const solution& best_sol);
    population crossover(const population& curr_pop, const population& curr_pop_v, double cr);
    population select(const population& curr_pop, const population& curr_pop_u, solution& curr_obj_vals, solution& curr_obj_vals_u, string function_name);

private:
    void init(population& curr_pop);

private:
    int num_runs;
    int num_evals;
    int num_dims;
    string filename_ini;
    string filename_ins;

    double best_obj_val;
    solution best_sol;

    // data members for population-based algorithms
    int pop_size;
    vector<double> curr_obj_vals;

    // data members for de-specific parameters
    double F;
    double cr;
    double vmin;
    double vmax;
};

inline de::de(int num_runs,
              int num_evals,
              int num_dims,
              string filename_ini,
              string filename_ins,
              int pop_size,
              double F,
              double cr,
              double vmin,
              double vmax
              )
    : num_runs(num_runs),
      num_evals(num_evals),
      num_dims(num_dims),
      filename_ini(filename_ini),
      filename_ins(filename_ins),
      pop_size(pop_size),
      F(F),
      cr(cr),
      vmin(vmin),
      vmax(vmax)
{
    srand();
}

inline de::population de::run()
{
    population curr_pop(pop_size, solution(num_dims, vmax));
    double avg_obj_val = 0.0;
    vector<double> avg_obj_val_eval(num_evals, 0.0);

    for (int r = 0; r < num_runs; r++) {
        int eval_count = 0;
        double best_so_far = numeric_limits<double>::max();

        // 0. initialization (also called initialisation)
        init(curr_pop);

        while (eval_count < num_evals) {
            // 1. mutation
            population curr_pop_v = mutate(curr_pop, F, vmin, vmax, best_sol);

            // 2. crossover
            population curr_pop_u = crossover(curr_pop, curr_pop_v, cr);

            // 3. evaluation
            vector<double> curr_obj_vals_u = evaluate(filename_ins, num_dims, curr_pop_u);

            // 4. selection
            curr_pop = select(curr_pop, curr_pop_u, curr_obj_vals, curr_obj_vals_u, filename_ins);

            for (size_t i = 0; i < curr_obj_vals.size(); i++) {
                if (best_so_far > curr_obj_vals[i]) {
                    best_so_far = curr_obj_vals[i];
                    best_sol = curr_pop[i];
                }
                if (eval_count < num_evals)
                    avg_obj_val_eval[eval_count++] += best_so_far;
            }
        }
        avg_obj_val += best_so_far;
    }

    avg_obj_val /= num_runs;

    for (int i = 0; i < num_evals; i++) {
        avg_obj_val_eval[i] /= num_runs;
        cout << fixed << setprecision(3) << avg_obj_val_eval[i]  << endl;
    }

    cout << best_sol << endl;

    return curr_pop;
}

inline void de::init(population& curr_pop)
{
    // 1. parameters initialization
    best_sol = vector<double>(num_dims, vmax);
    best_obj_val = numeric_limits<double>::max();
    curr_obj_vals = vector<double>(pop_size, numeric_limits<double>::max());

    // 2. initialize the positions and velocities of particles
    if (!filename_ini.empty()) {
        ifstream ifs(filename_ini.c_str());
        for (int p = 0; p < pop_size; p++) {
            for (int i = 0; i < num_dims; i++)
                ifs >> curr_pop[p][i];
        }
    }
    else {
        for (int p = 0; p < pop_size; p++)
            for (int i = 0; i < num_dims; i++)
                curr_pop[p][i] = vmin + (vmax - vmin) * rand() / (RAND_MAX + 1.0);
    }

    // 3. evaluate the initial population
    curr_obj_vals = evaluate(filename_ins, num_dims, curr_pop);
}

inline vector<double> de::evaluate(string function_name, int dims, const population& curr_pop)
{
    vector<double> obj_vals(curr_pop.size(), 0.0);
    const auto it = function_table.find(function_name);
    if (it != function_table.end()) {
        const auto& f = it->second;
        for (size_t i = 0; i < curr_pop.size(); i++)
            obj_vals[i] = f(curr_pop[i].size(), curr_pop[i]);
    }
    return obj_vals;
}

inline de::population de::mutate(const population& curr_pop, double F, double vmin, double vmax, const solution& best_sol)
{
    population new_pop(curr_pop.size(), solution(curr_pop[0].size()));
    for (size_t i = 0; i < curr_pop.size(); i++) {
        const solution& s1 = curr_pop[rand() % curr_pop.size()];
        const solution& s2 = curr_pop[rand() % curr_pop.size()];
        const solution& s3 = curr_pop[rand() % curr_pop.size()];
        for (size_t j = 0; j < curr_pop[i].size(); j++) {
            new_pop[i][j] = s1[j] + F * (s2[j]-s3[j]);
            if (new_pop[i][j] < vmin)
                new_pop[i][j] = vmin;
            if (new_pop[i][j] > vmax)
                new_pop[i][j] = vmax;
        }
    }
    return new_pop;
}

inline de::population de::crossover(const population& curr_pop, const population& curr_pop_v, double cr)
{
    population new_pop(curr_pop.size(), solution(curr_pop[0].size()));
    for (size_t i = 0; i < curr_pop.size(); i++) {
        const double s = rand() % curr_pop[0].size();
        for (size_t j = 0; j < curr_pop[i].size(); j++) {
            const double r = static_cast<double>(rand()) / RAND_MAX;
            new_pop[i][j] = (r < cr || s == j) ? curr_pop_v[i][j] : curr_pop[i][j];
        }
    }
    return new_pop;
}

inline de::population de::select(const population& curr_pop, const population& curr_pop_u, solution& curr_obj_vals, solution& curr_obj_vals_u, string function_name)
{
    population new_pop(curr_pop.size(), solution(curr_pop[0].size()));
    for (size_t i = 0; i < curr_pop.size(); i++) {
        if (curr_obj_vals_u[i] < curr_obj_vals[i]) {
            new_pop[i] = curr_pop_u[i];
            curr_obj_vals[i] = curr_obj_vals_u[i];
        }
        else {
            new_pop[i] = curr_pop[i];
        }
    }
    return new_pop;
}

#endif
