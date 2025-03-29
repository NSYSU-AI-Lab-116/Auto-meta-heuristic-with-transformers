#ifndef __DECB1_H_INCLUDED__
#define __DECB1_H_INCLUDED__

#include "de.h"

class decb1: public de
{
public:
    using de::de;

private:
    population mutate(const population& curr_pop, double F, double vmin, double vmax, const solution& best_sol) override;
};

inline decb1::population decb1::mutate(const population& curr_pop, double F, double vmin, double vmax, const solution& best_sol)
{
    population new_pop(curr_pop.size(), solution(curr_pop[0].size()));
    for (size_t i = 0; i < curr_pop.size(); i++) {
        const solution& s1 = curr_pop[rand() % curr_pop.size()];
        const solution& s2 = curr_pop[rand() % curr_pop.size()];

        for (size_t j = 0; j < curr_pop[i].size(); j++) {
            new_pop[i][j] = curr_pop[i][j] + (F * (best_sol[j]-curr_pop[i][j])) + (F * (s1[j]-s2[j]));
            if (new_pop[i][j] < vmin)
                new_pop[i][j] = vmin;
            if (new_pop[i][j] > vmax)
                new_pop[i][j] = vmax;
        }
    }
    return new_pop;
}

#endif
