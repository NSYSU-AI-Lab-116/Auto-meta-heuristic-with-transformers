#ifndef __GARXU_H_INCLUDED__
#define __GARXU_H_INCLUDED__

#include "gar.h"

class garxu: public gar
{
public:
    using gar::gar;

private:
    population crossover(population& curr_pop, double cr) override;
};


// uniform crossover
inline garxu::population garxu::crossover(population& curr_pop, double cr)
{
    const int mid = curr_pop.size()/2;
    for (int i = 0; i < mid; i++) {
        for (size_t j = 0; j < curr_pop[0].size(); j++) {
            const double f = static_cast<double>(rand()) / RAND_MAX;
            if (f <= 0.5) // yes, 0.5 instead of cr
                swap(curr_pop[i][j], curr_pop[mid+i][j]);
        }
    }
    return curr_pop;
}

#endif
