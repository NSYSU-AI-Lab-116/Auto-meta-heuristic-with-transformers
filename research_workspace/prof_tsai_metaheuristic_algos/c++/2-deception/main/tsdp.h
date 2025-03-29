#ifndef __TSDP_H_INCLUDED__
#define __TSDP_H_INCLUDED__

#include "ts.h"

class tsdp: public ts
{
public:
    using ts::ts;

protected:
    int evaluate(const solution& s) override;
    tuple<tsdp::solution, int, int> select_neighbor_not_in_tabu(const solution& s) override;
};


inline int tsdp::evaluate(const solution& s)
{
    eval_count++;
    int n = 0;
    for (size_t i = 0; i < s.size(); i++)
        n += s[i] << ((s.size() - 1) - i);
    return abs(n - (1 << (s.size()-2)));
}

inline tuple<tsdp::solution, int, int> tsdp::select_neighbor_not_in_tabu(const solution& s)
{
    auto[t, f_t, n_evals] = ts::select_neighbor_not_in_tabu(s);
    if (n_evals == 0) {
        do {
            for (size_t i = 0; i < s.size(); i++)
                t[i] = rand() % 2;
        } while (in_tabu(t));
        append_to_tabu_list(t);
        f_t = evaluate(t);
        n_evals = 1;
    }
    return make_tuple(t, f_t, n_evals);
}

#endif
