#ifndef __DEB2_H_INCLUDED__
#define __DEB2_H_INCLUDED__

#include "de.h"

class deb2: public de
{
public:
    using de::de;

private:
    population mutate(const population& curr_pop, double F, double vmin, double vmax, const solution& best_sol) override;
};

inline deb2::population deb2::mutate(const population& curr_pop, double F, double vmin, double vmax, const solution& best_sol)
{
    population new_pop(curr_pop.size(), solution(curr_pop[0].size()));
    for (size_t i = 0; i < curr_pop.size(); i++) {
        const solution& s1 = curr_pop[rand() % curr_pop.size()];
        const solution& s2 = curr_pop[rand() % curr_pop.size()];
        const solution& s3 = curr_pop[rand() % curr_pop.size()];
        const solution& s4 = curr_pop[rand() % curr_pop.size()];

        for (size_t j = 0; j < curr_pop[i].size(); j++) {
            new_pop[i][j] = best_sol[j] + (F * (s1[j]-s2[j])) + (F * (s3[j]-s4[j]));
            if (new_pop[i][j] < vmin)
                new_pop[i][j] = vmin;
            if (new_pop[i][j] > vmax)
                new_pop[i][j] = vmax;
        }
    }
    return new_pop;
}

#endif
