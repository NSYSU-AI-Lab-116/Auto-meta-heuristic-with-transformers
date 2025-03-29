#ifndef __GARDP_H_INCLUDED__
#define __GARDP_H_INCLUDED__

#include "gar.h"

class gardp: public gar
{
public:
    using gar::gar;

private:
    obj_val_type evaluate(const population& curr_pop) override;
};


inline gardp::obj_val_type gardp::evaluate(const population& curr_pop)
{
    const size_t pop_size = curr_pop.size();
    const size_t num_patterns_sol = curr_pop[0].size();
    vector<int> n(pop_size, 0);
    for (size_t p = 0; p < pop_size; p++){
        for (size_t i = 0; i < num_patterns_sol; i++)
            n[p] += curr_pop[p][i] << ((num_patterns_sol - 1) - i);
        n[p] = abs(n[p] - (1 << (num_patterns_sol-2)));
    }
    return n;
}

#endif
