#ifndef __GADP_H_INCLUDED__
#define __GADP_H_INCLUDED__

#include "ga.h"

class gadp: public ga
{
public:
    using ga::ga;

private:
    vector<int> evaluate(const population& curr_pop) override;
};


inline vector<int> gadp::evaluate(const population& curr_pop)
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
