#ifndef __GAX2_H_INCLUDED__
#define __GAX2_H_INCLUDED__

#include "ga.h"

class gax2: public ga
{
public:
    using ga::ga;

private:
    population crossover(population& curr_pop, double cr) override;
};


// two-point crossover
inline gax2::population gax2::crossover(population& curr_pop, double cr)
{
    const int mid = curr_pop.size()/2;
    for (int i = 0; i < mid; i++) {
        const double f = static_cast<double>(rand()) / RAND_MAX;
        if (f <= cr) {
            int xp1 = rand() % curr_pop[0].size(); // crossover point 1
            int xp2 = rand() % curr_pop[0].size(); // crossover point 2
            if (xp2 < xp1)
                swap(xp1, xp2);
            for (int j = xp1; j < xp2; j++)
                swap(curr_pop[i][j], curr_pop[mid+i][j]);
        }
    }
    return curr_pop;
}

#endif
