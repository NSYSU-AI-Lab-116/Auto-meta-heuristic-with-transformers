#ifndef __GAOX_H_INCLUDED__
#define __GAOX_H_INCLUDED__

#include "ga.h"

class gaox: public ga
{
public:
    using ga::ga;

private:
    population crossover(const population& curr_pop, double cr) override;
};

inline population gaox::crossover(const population& curr_pop, double cr)
{
    population tmp_pop = curr_pop;

    const int mid = curr_pop.size()/2;
    const size_t ssz = curr_pop[0].size();
    for (int i = 0; i < mid; i++) {
        const double f = static_cast<double>(rand()) / RAND_MAX;
        if (f <= cr) {
            // 1. create the mapping sections
            size_t xp1 = rand() % (ssz + 1);
            size_t xp2 = rand() % (ssz + 1);
            if (xp1 > xp2)
                swap(xp1, xp2);

            // 2. indices to the two parents and offspring
            const int p[2] = { i, i+mid };

            // 3. the main process of ox
            for (int k = 0; k < 2; k++) {
                const int c1 = p[k];
                const int c2 = p[1-k];

                // 4. mask the genes between xp1 and xp2
                const auto& s1 = curr_pop[c1];
                const auto& s2 = curr_pop[c2];
                vector<bool> msk1(ssz, false);
                for (size_t j = xp1; j < xp2; j++)
                    msk1[s1[j]] = true;
                vector<bool> msk2(ssz, false);
                for (size_t j = 0; j < ssz; j++)
                    msk2[j] = msk1[s2[j]];

                // 5. replace the genes that are not masked
                for (size_t j = xp2 % ssz, z = 0; z < ssz; z++) {
                    if (!msk2[z]) {
                        tmp_pop[c1][j] = s2[z];
                        j = (j+1) % ssz;
                    }
                }
            }
        }
    }

    return tmp_pop;
}

#endif
