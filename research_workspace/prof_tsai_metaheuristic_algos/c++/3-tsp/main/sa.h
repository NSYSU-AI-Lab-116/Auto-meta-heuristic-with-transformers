#ifndef __SA_H_INCLUDED__
#define __SA_H_INCLUDED__

#include <string>
#include <limits>
#include "lib.h"

using namespace std;

class sa
{
public:
    typedef vector<int> solution;
    typedef vector<double> dist_1d;
    typedef vector<dist_1d> dist_2d;

    sa(int num_runs,
       int num_evals,
       int num_patterns_sol,
       string filename_ini,
       double max_temp, // sa-specific parameter
       double min_temp, // sa-specific parameter
       dist_2d dist,
       bool continue_flag
       );

    solution run(solution& sol_orig, int& eval_count_orig, vector<double>& avg_obj_val_eval_orig, double& best_obj_val_orig, solution& best_sol_orig);

private:
    solution init();
    double evaluate(const solution &s, const dist_2d &dist);
    solution transit(const solution& s);
    // begin the sa functions
    bool determine(double tmp_obj_val, double obj_val, double temperature);
    double annealing(double temperature);
    // end the sa functions

private:
    int num_runs;
    int num_evals;
    int num_patterns_sol;
    string filename_ini;

    // begin the sa parameters
    double max_temp;
    double min_temp;
    // end the sa parameters

    dist_2d dist;
    bool continue_flag;

    solution best_sol;
    double best_obj_val;
    solution curr_sol;
    double curr_temp;
};

inline sa::sa(int num_runs,
              int num_evals,
              int num_patterns_sol,
              string filename_ini,
              double max_temp,  // sa-specific parameter
              double min_temp,  // sa-specific parameter
              dist_2d dist,
              bool continue_flag
              )
    : num_runs(num_runs),
      num_evals(num_evals),
      num_patterns_sol(num_patterns_sol),
      filename_ini(filename_ini),
      max_temp(max_temp),
      min_temp(min_temp),
      dist(dist),
      continue_flag(continue_flag)
{
    srand();
}

inline sa::solution sa::run(solution& sol_orig, int& eval_count_orig, vector<double>& avg_obj_val_eval_orig, double& best_obj_val_orig, solution& best_sol_orig)
{
    const int eval_count_saved = eval_count_orig;

    for (int r = 0; r < num_runs; r++) {
        int eval_count = eval_count_saved;

        // 0. Initialization
        curr_sol = init();

        best_obj_val = best_obj_val_orig;
        best_sol = best_sol_orig;
        curr_sol = sol_orig;

        double obj_val = evaluate(curr_sol, dist);

        while (eval_count < num_evals + eval_count_saved) {
            // 1. Transition
            solution tmp_sol = transit(curr_sol);

            // 2. Evaluation
            double tmp_obj_val = evaluate(tmp_sol, dist);

            // 3. Determination
            if (determine(tmp_obj_val, obj_val, curr_temp)) {
                curr_sol = tmp_sol;
                obj_val = tmp_obj_val;
            }

            if (obj_val < best_obj_val) {
                best_sol = curr_sol;
                best_obj_val = obj_val;
            }

            curr_temp = annealing(curr_temp);
            avg_obj_val_eval_orig[eval_count++] += best_obj_val;
        }

        eval_count_orig =  eval_count;

        if (best_obj_val < best_obj_val_orig) {
            best_obj_val_orig = best_obj_val;
            best_sol_orig = best_sol;
            sol_orig = best_sol;
        }
        else
            sol_orig = curr_sol;
    }

    return sol_orig;
}


inline sa::solution sa::init()
{
    curr_temp = max_temp;

    if (!continue_flag) {
        curr_sol = solution(num_patterns_sol);
        for (int i = 0; i < num_patterns_sol; i++)
            curr_sol[i] = i;
        for (int i = num_patterns_sol-1; i > 0; --i)    // shuffle the solutions
            swap(curr_sol[i], curr_sol[rand() % (i+1)]);
    }

    return curr_sol;
}

inline sa::solution sa::transit(const solution& s)
{
    solution t(s);
    const int i = rand() % s.size();
    const int j = rand() % s.size();
    swap(t[i], t[j]);
    return t;
}

inline double sa::evaluate(const solution &s, const dist_2d &dist)
{
    double tour_dist = 0.0;
    for (size_t i = 0; i < s.size(); i++){
        const int c = s[i];
        const int n = s[(i+1) % s.size()];
        tour_dist += dist[c][n];
    }
    return tour_dist;
}

inline bool sa::determine(double tmp_obj_val, double obj_val, double temperature)
{
    const double r = static_cast<double>(rand()) / RAND_MAX;
    const double p = exp((tmp_obj_val - obj_val) / temperature);
    return r > p;
}

inline double sa::annealing(double temperature)
{
    return 0.9 * temperature;
}
#endif
