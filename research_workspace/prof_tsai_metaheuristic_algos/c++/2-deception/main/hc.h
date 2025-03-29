#ifndef __HC_H_INCLUDED__
#define __HC_H_INCLUDED__

#include <string>
#include <fstream>
#include <numeric>
#include "lib.h"

using namespace std;

class hc
{
public:
    typedef vector<int> solution;

    hc(int num_runs,
       int num_evals,
       int num_patterns_sol,
       string filename_ini);

    virtual ~hc() {}

    solution run();

private:
    void init();
    virtual int evaluate(const solution& s);
    virtual solution transit(const solution& s);
    virtual void determine(const solution& v, int fv, solution& s, int &fs);

private:
    int d_num_runs;
    int d_num_evals;
    int d_num_patterns_sol;
    string d_filename_ini;

    solution d_sol;
    int d_obj_val;
};

inline hc::hc(int num_runs,
              int num_evals,
              int num_patterns_sol,
              string filename_ini)
    : d_num_runs(num_runs),
      d_num_evals(num_evals),
      d_num_patterns_sol(num_patterns_sol),
      d_filename_ini(filename_ini)
{
    srand();
}

inline hc::solution hc::run()
{
    double d_avg_obj_val = 0;
    vector<double> d_avg_obj_val_eval(d_num_evals, 0.0);

    for (int r = 0; r < d_num_runs; r++) {
        int eval_count = 0;

        // 0. Initialization
        init();
        d_obj_val = evaluate(d_sol);
        d_avg_obj_val_eval[eval_count++] += d_obj_val;

        while (eval_count < d_num_evals) {
            // 1. Transition
            solution tmp_sol = transit(d_sol);

            // 2. Evaluation
            int tmp_obj_val = evaluate(tmp_sol);

            // 3. Determination
            determine(tmp_sol, tmp_obj_val, d_sol, d_obj_val);

            d_avg_obj_val_eval[eval_count++] += d_obj_val;
        }
        d_avg_obj_val += d_obj_val;
    }

    // 4. Output
    d_avg_obj_val /= d_num_runs;

    for (int i = 0; i < d_num_evals; i++) {
        d_avg_obj_val_eval[i] /= d_num_runs;
        cout << fixed << setprecision(3) << d_avg_obj_val_eval[i] << endl;
    }

    return d_sol;
}

inline void hc::init()
{
    d_sol = solution(d_num_patterns_sol);

    if (!d_filename_ini.empty()) {
        ifstream ifs(d_filename_ini.c_str());
        for (int i = 0; i < d_num_patterns_sol; i++)
            ifs >> d_sol[i];
    }
    else {
        for (int i = 0; i < d_num_patterns_sol; i++)
            d_sol[i] = rand() % 2;
    }
}

inline hc::solution hc::transit(const solution& s)
{
    return ::transit(s);
}

inline int hc::evaluate(const solution& s)
{
    return accumulate(s.begin(), s.end(), 0);
}

inline void hc::determine(const solution& v, int fv, solution& s, int &fs)
{
    if (fv > fs) {
        fs = fv;
        s = v;
    }
}

#endif
