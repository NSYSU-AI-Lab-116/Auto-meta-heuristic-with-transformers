#ifndef __SA_REFINIT_H_INCLUDED__
#define __SA_REFINIT_H_INCLUDED__

#include <iostream>
#include <string>
#include <fstream>
#include <numeric>
#include "lib.h"

using namespace std;

class sa_refinit
{
public:
    typedef vector<int> solution;

    sa_refinit(int num_runs,
               int num_evals,
               int num_patterns_sol,
               string filename_ini,
               double min_temp, // sa-specific parameter
               double max_temp, // sa-specific parameter
               int num_samplings,
               int num_same_bits
               );

    virtual ~sa_refinit() {}

    solution run();

private:
    void init(vector<double>& avg_obj_val_eval);
    virtual int evaluate(const solution& s);
    virtual solution transit(const solution& s);

    // begin the sa functions
    bool determine(int tmp_obj_val, int obj_val, double temperature);
    double annealing(double temperature);
    // end the sa functions

private:
    int num_runs;
    int num_evals;
    int num_patterns_sol;
    string filename_ini;

    solution sol;
    int obj_val;

    solution best_sol;
    int best_obj_val;

    // begin the sa parameters
    double min_temp;
    double max_temp;
    double curr_temp;
    // end the sa parameters
    int num_samplings;
    int num_same_bits;
};

inline sa_refinit::sa_refinit(int num_runs,
                              int num_evals,
                              int num_patterns_sol,
                              string filename_ini,
                              double min_temp,  // sa-specific parameter
                              double max_temp,  // sa-specific parameter
                              int num_samplings,
                              int num_same_bits
                              )
    : num_runs(num_runs),
      num_evals(num_evals),
      num_patterns_sol(num_patterns_sol),
      filename_ini(filename_ini),
      min_temp(min_temp),
      max_temp(max_temp),
      num_samplings(num_samplings),
      num_same_bits(num_same_bits)
{
    srand();
}

inline sa_refinit::solution sa_refinit::run()
{
    double avg_obj_val = 0;
    vector<double> avg_obj_val_eval(num_evals, 0);

    for (int r = 0; r < num_runs; r++) {
        int eval_count = num_samplings;

        // 0. Initialization
        init(avg_obj_val_eval);
        obj_val = evaluate(sol);

        while (eval_count < num_evals) {
            // 1. Transition
            solution tmp_sol = transit(sol);

            // 2. Evaluation
            int tmp_obj_val = evaluate(tmp_sol);

            // 3. Determination
            if (determine(tmp_obj_val, obj_val, curr_temp)) {
                obj_val = tmp_obj_val;
                sol = tmp_sol;
            }

            if (obj_val > best_obj_val) {
                best_obj_val = obj_val;
                best_sol = sol;
            }

            curr_temp = annealing(curr_temp);

            avg_obj_val_eval[eval_count++] += best_obj_val;
        }
        avg_obj_val += best_obj_val;
    }

    // 4. Output
    avg_obj_val /= num_runs;

    for (int i = 0; i < num_evals; i++) {
        avg_obj_val_eval[i] /= num_runs;
        cout << fixed << setprecision(3) << avg_obj_val_eval[i] << endl;
    }

    return sol;
}

inline void sa_refinit::init(vector<double>& avg_obj_val_eval)
{
    curr_temp = max_temp;
    best_obj_val = 0;

    sol = solution(num_patterns_sol);

    if (!filename_ini.empty()) {
        ifstream ifs(filename_ini.c_str());
        for (size_t i = 0; i < sol.size(); i++)
            ifs >> sol[i];
    }
    else {
        solution tmp_sol(num_patterns_sol);

        for (int j = 0; j < num_samplings; j++) {
            for (int i = 0; i < num_patterns_sol; i += num_same_bits)
                fill_n(tmp_sol.begin()+i, num_same_bits, rand() % 2);

            int tmp_obj_val = evaluate(tmp_sol);

            if (j == 0 || tmp_obj_val > obj_val) {
                best_obj_val = obj_val = tmp_obj_val;
                sol = tmp_sol;
            }
            avg_obj_val_eval[j] += obj_val;
        }
    }
}

inline sa_refinit::solution sa_refinit::transit(const solution& s)
{
    return ::transit_r(s);
}

inline int sa_refinit::evaluate(const solution& s)
{
    return accumulate(s.begin(), s.end(), 0);
}

inline bool sa_refinit::determine(int tmp_obj_val, int obj_val, double temperature)
{
    const double r = static_cast<double>(rand()) / RAND_MAX;
    const double p = exp((tmp_obj_val - obj_val)/temperature);
    return r < p;
}

inline double sa_refinit::annealing(double temperature)
{
    return 0.9 * temperature;
}

#endif
