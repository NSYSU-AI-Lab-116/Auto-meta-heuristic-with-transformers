#ifndef __GAR_H_INCLUDED__
#define __GAR_H_INCLUDED__

#include "ga.h"

class gar: public ga
{
public:
    using ga::ga;

private:
    population select(const population& curr_pop, const obj_val_type& curr_obj_vals, int num_players) override;
};

// roulette wheel selection
inline gar::population gar::select(const population& curr_pop, const obj_val_type& curr_obj_vals, int num_players)
{
#if 1
    // 1. compute the probabilities of the roulette wheel
    const double total = accumulate(curr_obj_vals.begin(), curr_obj_vals.end(), 0);
    vector<double> prob(curr_pop.size());
    for (size_t i = 0; i < curr_pop.size(); i++)
        prob[i] = curr_obj_vals[i] / total;

    // 2. select the individuals for the next generation
    population tmp_pop(curr_pop.size());
    for (size_t i = 0; i < curr_pop.size(); i++) {
        double f = static_cast<double>(rand()) / RAND_MAX;
        for (size_t j = 0; j < curr_pop.size(); j++) {
            if ((f -= prob[j]) <= 0) {
                tmp_pop[i] = curr_pop[j];
                break;
            }
        }
    }
    return tmp_pop;
#else
    // a simpler implementation
    const double total = accumulate(curr_obj_vals.begin(), curr_obj_vals.end(), 0);
    population tmp_pop(curr_pop.size());
    for (size_t i = 0; i < curr_pop.size(); i++) {
        double f = total * static_cast<double>(rand()) / RAND_MAX;
        for (size_t j = 0; j < curr_pop.size(); j++) {
            if ((f -= curr_obj_vals[j]) <= 0) {
                tmp_pop[i] = curr_pop[j];
                break;
            }
        }
    }
    return tmp_pop;
#endif
}

#endif
