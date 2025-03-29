#ifndef __GAPMX_H_INCLUDED__
#define __GAPMX_H_INCLUDED__

#include "ga.h"

class gapmx: public ga
{
public:
    using ga::ga;

private:
    population crossover(const population& curr_pop, double cr) override;
};

inline population gapmx::crossover(const population& curr_pop, double cr)
{
    population tmp_pop = curr_pop;

    const int mid = curr_pop.size()/2;
    for (int i = 0; i < mid; i++) {
        const double f = static_cast<double>(rand()) / RAND_MAX;
        if (f <= cr) {
            // 1. select the two parents and offspring
            const int p[2] = { i, i+mid };

            // 2. select the mapping sections
            size_t xp1 = rand() % (curr_pop[0].size() + 1);
            size_t xp2 = rand() % (curr_pop[0].size() + 1);
            if (xp1 > xp2)
                swap(xp1, xp2);

            // 3. swap the mapping sections
            for (size_t j = xp1; j < xp2; j++)
                swap(tmp_pop[p[0]][j], tmp_pop[p[1]][j]);

            // 4. fix the duplicates
            for (int k = 0; k < 2; k++) {
                const int z = p[k];
                for (size_t j = 0; j < curr_pop[0].size(); j++) {
                    if (j < xp1 || j >= xp2) {
                        int c = curr_pop[z][j];
                        size_t m = xp1;
                        while (m < xp2) {
                            if (c == tmp_pop[z][m]) {
                                c = curr_pop[z][m];
                                m = xp1; // restart the while loop
                            }
                            else
                                m++; // move on to the next
                        }
                        if (c != curr_pop[z][j])
                            tmp_pop[z][j] = c;
                    }
                }
            }
        }
    }

    return tmp_pop;
}

#endif
