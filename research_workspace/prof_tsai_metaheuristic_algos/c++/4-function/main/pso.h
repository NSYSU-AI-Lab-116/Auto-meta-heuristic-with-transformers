#ifndef __PSO_H_INCLUDED__
#define __PSO_H_INCLUDED__

#include <iostream>
#include <fstream>
#include <limits>
#include "pso.h"
#include "lib.h"
#include "functions.h"

using namespace std;

class pso
{
public:
    using solution = vector<double>;
    using population = vector<solution>;

    pso(int num_runs,
        int num_evals,
        int num_dims,
        string filename_ini,
        string filename_ins,
        int pop_size,
        double omega,
        double c1,
        double c2,
        double vmin,
        double vmax);

    population run();

    vector<double> evaluate(string function_name, int dims, const population& curr_pop);
    population new_velocity(const population& curr_pop, population& velocity, population& pbest, solution& gbest, double omega, double c1, double c2, double vmin, double vmax);
    population new_position(population& curr_pop, population& velocity, double vmin, double vmax);

private:
    void init();
    void update_pb(vector<double>& pbest_obj_vals, vector<double>& curr_obj_vals);
    void update_gb(double& gbest_obj_val, vector<double>& curr_obj_vals);
    void update_best_sol(const double& gbest_obj_val, const solution& gbest);

private:
    int num_runs;
    int num_evals;
    int num_dims;
    string filename_ini;
    string filename_ins;

    double avg_obj_val;
    vector<double> avg_obj_val_eval;
    double best_obj_val;
    solution best_sol;

    // data members for population-based algorithms
    int pop_size;
    population curr_pop;
    population velocity;
    vector<double> curr_obj_vals;

    // data members for pso-specific parameters
    population pbest;
    solution gbest;
    vector<double> pbest_obj_vals;
    double gbest_obj_val;

    double omega;
    double c1;
    double c2;
    double vmin;
    double vmax;
};

inline pso::pso(int num_runs,
                int num_evals,
                int num_dims,
                string filename_ini,
                string filename_ins,
                int pop_size,
                double omega,
                double c1,
                double c2,
                double vmin,
                double vmax
                )
    : num_runs(num_runs),
      num_evals(num_evals),
      num_dims(num_dims),
      filename_ini(filename_ini),
      filename_ins(filename_ins),
      pop_size(pop_size),
      omega(omega),
      c1(c1),
      c2(c2),
      vmin(vmin),
      vmax(vmax)
{
    srand();
}

inline pso::population pso::run()
{
    avg_obj_val = 0.0;
    vector<double> avg_obj_val_eval(num_evals, 0.0);

    for (int r = 0; r < num_runs; r++) {
        int eval_count = 0;
        double best_so_far = numeric_limits<double>::max();

        // 0. initialization
        init();

        while (eval_count < num_evals) {
            // 1. compute new velocity of each particle
            velocity = new_velocity(curr_pop, velocity, pbest, gbest, omega, c1, c2, vmin, vmax);

            // 2. adjust all the particles to their new positions
            curr_pop = new_position(curr_pop, velocity, vmin, vmax);

            // 3. evaluation
            curr_obj_vals = evaluate(filename_ins, num_dims, curr_pop);

            for (size_t i = 0; i < curr_obj_vals.size(); i++) {
                if (best_so_far > curr_obj_vals[i])
                    best_so_far = curr_obj_vals[i];
                if (eval_count < num_evals)
                    avg_obj_val_eval[eval_count++] += best_so_far;
            }

            // 4. update
            update_pb(pbest_obj_vals, curr_obj_vals);
            update_gb(gbest_obj_val, curr_obj_vals);
            update_best_sol(gbest_obj_val, gbest);
        }
        avg_obj_val += best_obj_val;
    }

    avg_obj_val /= num_runs;

    for (int i = 0; i < num_evals; i++) {
        avg_obj_val_eval[i] /= num_runs;
        cout << fixed << setprecision(3) << avg_obj_val_eval[i]  << endl;
    }

    cout << best_sol << endl;

    return curr_pop;
}

inline void pso::init()
{
    // 1. parameters initialization
    curr_pop = population(pop_size, solution(num_dims, vmax));
    velocity = population(pop_size, solution(num_dims, vmax));
    pbest = population(pop_size, solution(num_dims, vmax));
    pbest_obj_vals = vector<double>(pop_size, numeric_limits<double>::max());
    gbest = solution(num_dims, vmax);
    gbest_obj_val = numeric_limits<double>::max();
    curr_obj_vals = vector<double>(pop_size, numeric_limits<double>::max());
    best_sol = vector<double>(num_dims, vmax);
    best_obj_val = numeric_limits<double>::max();

    // 2. initialize the positions and velocities of particles
    if (!filename_ini.empty()) {
        ifstream ifs(filename_ini.c_str());
        for (int p = 0; p < pop_size; p++) {
            for (int i = 0; i < num_dims; i++) {
                ifs >> curr_pop[p][i] >> velocity[p][i];
            }
        }
    }
    else {
        for (int p = 0; p < pop_size; p++)
            for (int i = 0; i < num_dims; i++) {
                curr_pop[p][i] = vmin + (vmax - vmin) * rand() / (RAND_MAX + 1.0);
                velocity[p][i] = curr_pop[p][i] / num_evals;
            }
    }

    // 3. evaluation
    curr_obj_vals = evaluate(filename_ins, num_dims, curr_pop);

    // 4. update
    update_pb(pbest_obj_vals, curr_obj_vals);
    update_gb(gbest_obj_val, curr_obj_vals);
    update_best_sol(gbest_obj_val, gbest);
}

inline vector<double> pso::evaluate(string function_name, int dims, const population& curr_pop)
{
    vector<double> obj_vals(pop_size, 0.0);
    auto it = function_table.find(function_name);
    if (it != function_table.end()) {
        const auto& f = it->second;
        for (size_t i = 0; i < curr_pop.size(); i++)
            obj_vals[i] = f(curr_pop[i].size(), curr_pop[i]);
    }
    return obj_vals;
}

inline void pso::update_pb(vector<double>& pbest_obj_vals, vector<double>& curr_obj_vals)
{
    for (size_t i = 0; i < curr_obj_vals.size(); i++)   {
        if (curr_obj_vals[i] < pbest_obj_vals[i]) {
            pbest_obj_vals[i] = curr_obj_vals[i];
            pbest[i] = curr_pop[i];
        }
    }
}

inline void pso::update_gb(double& gbest_obj_val, vector<double>& curr_obj_vals)
{
    for (size_t i = 0; i < curr_obj_vals.size(); i++) {
        if (curr_obj_vals[i] < gbest_obj_val) {
            gbest_obj_val = curr_obj_vals[i];
            gbest = curr_pop[i];
        }
    }
}

inline void pso::update_best_sol(const double& gbest_obj_val, const solution& gbest)
{
    if (gbest_obj_val < best_obj_val) {
        best_obj_val = gbest_obj_val;
        for (size_t i = 0; i < gbest.size(); i++)
            best_sol[i] = gbest[i];
    }
}

inline pso::population pso::new_velocity(const population& curr_pop, population& velocity, population& pbest, solution& gbest, double omega, double c1, double c2, double vmin, double vmax)
{
    population new_v(curr_pop.size(), solution(curr_pop[0].size()));
    for (size_t i = 0; i < curr_pop.size(); i++) {
        for (size_t j = 0; j < curr_pop[i].size(); j++) {
            double r1 = static_cast<double>(rand()) / RAND_MAX;
            double r2 = static_cast<double>(rand()) / RAND_MAX;
            new_v[i][j] = omega * velocity[i][j] + c1 * r1 * (pbest[i][j] - curr_pop[i][j]) + c2 * r2 * (gbest[j] - curr_pop[i][j]);
            if (new_v[i][j] < vmin)
                new_v[i][j] = vmin;
            else if (new_v[i][j] > vmax)
                new_v[i][j] = vmax;
        }
    }
    return new_v;
}

inline pso::population pso::new_position(population& curr_pop, population& velocity, double vmin, double vmax)
{
    population new_pos(curr_pop.size(), solution(curr_pop[0].size()));
    for (size_t i = 0; i < curr_pop.size(); i++) {
        for (size_t j = 0; j < curr_pop[i].size(); j++) {
            new_pos[i][j] = curr_pop[i][j] + velocity[i][j];
            if (new_pos[i][j] < vmin)
                new_pos[i][j] = vmin;
            else if (new_pos[i][j] > vmax)
                new_pos[i][j] = vmax;
        }
    }
    return new_pos;
}

#endif
