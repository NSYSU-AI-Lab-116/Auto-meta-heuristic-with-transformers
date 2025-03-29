#ifndef __GACX_H_INCLUDED__
#define __GACX_H_INCLUDED__

#include "ga.h"

class gacx: public ga
{
public:
    using ga::ga;

private:
    population crossover(const population& curr_pop, double cr) override;
};

inline population gacx::crossover(const population& curr_pop, double cr)
{
    population tmp_pop = curr_pop;

    const int mid = curr_pop.size()/2;
    const size_t ssz = curr_pop[0].size();
    for (int i = 0; i < mid; i++) {
        const double f = static_cast<double>(rand()) / RAND_MAX;
        if (f <= cr) {
            vector<bool> mask(ssz, false);
            const int c1 = i;
            const int c2 = i+mid;
            int c = tmp_pop[c1][0];
            int n = tmp_pop[c2][0];
            mask[0] = true;
            while (c != n) {
                for (size_t j = 0; j < ssz; j++) {
                    if (n == tmp_pop[c1][j]) {
                        if (mask[j])
                            goto swap;
                        c = n;
                        n = tmp_pop[c2][j];
                        mask[j] = true;
                        break;
                    }
                }
            }
        swap:
            for (size_t j = 0; j < ssz; j++) {
                if (!mask[j])
                    swap(tmp_pop[c1][j], tmp_pop[c2][j]);
            }
        }
    }

    return tmp_pop;
}

#endif
