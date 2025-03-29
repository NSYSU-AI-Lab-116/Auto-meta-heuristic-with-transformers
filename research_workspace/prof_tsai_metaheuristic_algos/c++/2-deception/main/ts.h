#ifndef __TS_H_INCLUDED__
#define __TS_H_INCLUDED__

#include <iostream>
#include <string>
#include <fstream>
#include <numeric>
#include "lib.h"

using namespace std;

class ts
{
public:
    typedef vector<int> solution;       // ts-specific vector
    typedef vector<solution> tabu_list; // ts-specific vector

    ts(int num_runs,
       int num_evals,
       int num_patterns_sol,
       string filename_ini,
       int num_neighbors, // ts-specific parameter
       int siz_tabulist   // ts-specific parameter
       );

    virtual ~ts() {};

    solution run();

protected:
    int eval_count;

private:
    void init();
    virtual solution transit(const solution& s);

protected:
    virtual int evaluate(const solution& s);

    // begin the ts functions
    virtual tuple<solution, int, int> select_neighbor_not_in_tabu(const solution& s);
    bool in_tabu(const solution& s);
    void append_to_tabu_list(const solution& s);
    // end the ts functions

private:
    int num_runs;
    int num_evals;
    int num_patterns_sol;
    string filename_ini;

    solution sol;
    int obj_val;

    solution best_sol;
    int best_obj_val;

    // begin the ts parameters
    int num_neighbors;
    tabu_list tabulist;
    int siz_tabulist;
    // end the ts parameters
};

// begin the auxiliary function
inline bool operator==(const ts::solution& s1, const ts::solution& s2)
{
    for (size_t i = 0; i < s1.size(); i++)
        if (s1[i] != s2[i])
            return false;
    return true;
}
// end the auxiliary function

inline ts::ts(int num_runs,
              int num_evals,
              int num_patterns_sol,
              string filename_ini,
              int num_neighbors, // ts-specific parameter
              int siz_tabulist   // ts-specific parameter
              )
    : num_runs(num_runs),
      num_evals(num_evals),
      num_patterns_sol(num_patterns_sol),
      filename_ini(filename_ini),
      num_neighbors(num_neighbors),
      siz_tabulist(siz_tabulist)
{
    srand();
}

inline ts::solution ts::run()
{
    double avg_obj_val = 0;
    vector<double> avg_obj_val_eval(num_evals, 0.0);

    for (int r = 0; r < num_runs; r++) {
        // 0. initialization
        init();
        obj_val = evaluate(sol);
        eval_count = 0;
        avg_obj_val_eval[0] += obj_val;

        while (eval_count < num_evals-1) {
            // 1. transition and evaluation
            auto[tmp_sol, tmp_obj_val, n_evals] = select_neighbor_not_in_tabu(sol);
            if (n_evals > 0) {
                // 2. determination
                if (tmp_obj_val > obj_val) {
                    sol = tmp_sol;
                    obj_val = tmp_obj_val;
                }

                if (obj_val > best_obj_val) {
                    best_obj_val = obj_val;
                    best_sol = sol;
                }

                avg_obj_val_eval[eval_count] += best_obj_val;
                for (int i = 1; i < n_evals; i++)
                    avg_obj_val_eval[eval_count-i] = avg_obj_val_eval[eval_count];
            }
        }
        avg_obj_val += best_obj_val;
    }

    avg_obj_val /= num_runs;

    for (int i = 0; i < num_evals; i++) {
        avg_obj_val_eval[i] /= num_runs;
        cout << fixed << setprecision(3) << avg_obj_val_eval[i] << endl;
    }

    return sol;
}

inline void ts::init()
{
    tabulist = tabu_list(siz_tabulist, solution(num_patterns_sol));
    best_obj_val = 0;
    eval_count = 0;

    sol = solution(num_patterns_sol);
    if (!filename_ini.empty()) {
        ifstream ifs(filename_ini.c_str());
        for (int i = 0; i < num_patterns_sol; i++)
            ifs >> sol[i];
    }
    else {
        for (int i = 0; i < num_patterns_sol; i++)
            sol[i] = rand() % 2;
    }
}

inline ts::solution ts::transit(const solution& s)
{
    return ::transit_r(s);
}

inline tuple<ts::solution, int, int> ts::select_neighbor_not_in_tabu(const solution& s)
{
    int n_evals = 0;
    int f_t = 0;
    solution t(num_patterns_sol);
    for (int i = 0; i < num_neighbors; i++) {
        solution v = transit(s);
        if (!in_tabu(v)) {
            n_evals++;
            int f_v = evaluate(v);
            if (f_v > f_t) {
                f_t = f_v;
                t = v;
            }
            if (eval_count >= num_evals-1)
                break;
        }
    }
    if (n_evals > 0)
        append_to_tabu_list(t);
    return make_tuple(t, f_t, n_evals);
}

inline bool ts::in_tabu(const solution& s)
{
    for (size_t i = 0; i < tabulist.size(); i++)
        if (tabulist[i] == s)
            return true;
    return false;
}

inline int ts::evaluate(const solution& s)
{
    eval_count++;
    return accumulate(s.begin(), s.end(), 0);
}

inline void ts::append_to_tabu_list(const solution& s)
{
    tabulist.push_back(s);
    if (static_cast<int>(tabulist.size()) >= siz_tabulist)
        tabulist.erase(tabulist.begin());
}

#endif
