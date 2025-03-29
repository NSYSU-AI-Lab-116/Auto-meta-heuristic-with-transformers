#ifndef __PREGA_H_INCLUDED__
#define __PREGA_H_INCLUDED__

#include <string>
#include <fstream>
#include <limits>
#include "lib.h"

using namespace std;

class prega
{
public:
    typedef vector<int> solution;
    typedef vector<solution> population;
    typedef vector<bool> sol_mask;
    typedef vector<sol_mask> pop_mask;
    typedef vector<double> pattern;
    typedef vector<pattern> instance;
    typedef vector<instance> instances;
    typedef vector<double> obj_val_type;
    typedef vector<population> population_conv; // pra

    prega(int num_runs,
          int num_evals,
          int num_patterns_sol,
          int num_dims,
          int num_clusters,
          string filename_ini,
          string filename_ins,
          int pop_size,
          double crossover_rate,
          double mutation_rate,
          int num_players,
          int num_detections,
          double reduction_rate,
          int pra);

    population run();

    // begin the ga functions
    population crossover(population& curr_pop, double cr, pop_mask& pr_mask);
    population mutate(population& curr_pop, double mr, pop_mask& pr_mask);
    population okm(population& curr_pop, pop_mask& pr_mask, int eval);
    pop_mask detection(population& curr_pop, pop_mask& pr_mask, int eval);
    population select(population& curr_pop, obj_val_type& curr_obj_vals);
    population tournament_select(population& curr_pop, obj_val_type& curr_obj_vals, int num_players);
    // end the ga functions

private:
    void init();
    obj_val_type evaluate(const population& curr_pop);
    void update_best_sol(const population& curr_pop, const obj_val_type& curr_obj_vals);

    void redundant_analysis_1(const int curr_gen);
    void redundant_analysis_2(const int curr_gen, const int curr_run);

private:
    int num_runs;
    int num_evals;
    int num_patterns_sol;
    int num_dims;
    int num_clusters;
    string filename_ini;
    string filename_ins;

    double avg_obj_val;
    obj_val_type avg_obj_val_eval;
    double best_obj_val;
    solution best_sol;

    instance ins_clustering;
    instances centroids;

    // for population-based algorithms-begin
    population curr_pop;
    obj_val_type curr_obj_vals;
    // for population-based algorithms-end

    // ga parameters-begin
    int pop_size;
    double crossover_rate;
    double mutation_rate;
    int num_players;
    // ga parameters-end

    // pr-begin
    instance centroid_dist;
    pop_mask pr_mask;
    int num_detections;
    double reduction_rate;
    // pr-end

    // pra: redundant analysis-begin
    int pra;
    int curr_gen;
    population_conv pop_conv;
    population_conv final_state;
    instance  avg_final_state;
    pattern  all_final_state;
    // pra: redundant analysis-end
};

prega::prega(int num_runs,
             int num_evals,
             int num_patterns_sol,
             int num_dims,
             int num_clusters,
             string filename_ini,
             string filename_ins,
             int pop_size,
             double crossover_rate,
             double mutation_rate,
             int num_players,
             int num_detections,
             double reduction_rate,
             int pra
             )
    : num_runs(num_runs),
      num_evals(num_evals),
      num_patterns_sol(num_patterns_sol),
      num_dims(num_dims),
      num_clusters(num_clusters),
      filename_ini(filename_ini),
      filename_ins(filename_ins),
      pop_size(pop_size),
      crossover_rate(crossover_rate),
      mutation_rate(mutation_rate),
      num_players(num_players),
      num_detections(num_detections),
      reduction_rate(reduction_rate),
      pra(pra)
{
    srand();
}

prega::population prega::run()
{
    avg_obj_val = 0.0;
    obj_val_type avg_obj_val_eval(num_evals, 0.0);
    obj_val_type pr_kcounter(num_evals, 0.0);

    if (pra) {
        avg_final_state = instance(num_runs, pattern(num_evals/pop_size, 0.0));
        all_final_state = pattern(num_evals/pop_size, 0.0);
    }

    for (int r = 0; r < num_runs; r++) {
        int eval_count = 0;
        double best_so_far = numeric_limits<double>::max();

        // 0. initialization
        init();

        while (eval_count < num_evals) {
            // 1. evaluation
            curr_obj_vals = evaluate(curr_pop);
            update_best_sol(curr_pop, curr_obj_vals);

            if (pra) {
                redundant_analysis_1(curr_gen++);
                for (int p = 0; p < pop_size; p++) {
                    for (int i = 0; i < num_patterns_sol; i++)
                        if (pr_mask[p][i])
                            pr_kcounter[p+eval_count]++;
                }
            }

            for (int i = 0; i < pop_size; i++) {
                if (best_so_far > curr_obj_vals[i])
                    best_so_far = curr_obj_vals[i];
                if (eval_count < num_evals)
                    avg_obj_val_eval[eval_count++] += best_so_far;
            }

            // 2. determination
            curr_pop = tournament_select(curr_pop, curr_obj_vals, num_players);

            // 3. transition
            curr_pop = crossover(curr_pop, crossover_rate, pr_mask);
            curr_pop = mutate(curr_pop, mutation_rate, pr_mask);
            curr_pop = okm(curr_pop, pr_mask, eval_count);

            if (eval_count > num_detections)
                pr_mask = detection(curr_pop, pr_mask, (eval_count + pop_size) / pop_size);
        }

        avg_obj_val += best_obj_val;

        if (pra)
            redundant_analysis_2(curr_gen, r);
    }

    avg_obj_val /= num_runs;

    cout << fixed << setprecision(3);
    for (int i = 0; i < num_evals; i++) {
        avg_obj_val_eval[i] /= num_runs;
        cout << avg_obj_val_eval[i];
        if (pra)
            cout << ", " << pr_kcounter[i] / (num_runs * num_patterns_sol);
        cout << endl;
    }

    return curr_pop;
}

void prega::init()
{
    curr_pop = population(pop_size, solution(num_patterns_sol));
    ins_clustering = instance(num_patterns_sol, pattern(num_dims, 0.0));
    centroids = instances(pop_size, instance(num_clusters, pattern(num_dims, 0.0)));
    obj_val_type curr_obj_vals(pop_size, 0.0);
    best_obj_val = numeric_limits<double>::max();
    centroid_dist = instance(pop_size, pattern(num_clusters, 0.0));
    pr_mask = pop_mask(pop_size, sol_mask(num_patterns_sol, false));

    // pra: redundant analysis-begin
    if (pra) {
        pop_conv = population_conv((num_evals/pop_size), population(pop_size, solution(num_patterns_sol, 0)));
        final_state = population_conv(num_runs, population(pop_size, solution(num_patterns_sol, 0)));
        curr_gen = 0;
    }
    // pra: redundant analysis-end

    // 1. input the dataset to be clustered
    if (!filename_ins.empty()) {
        ifstream ifs(filename_ins.c_str());
        for (int i = 0; i < num_patterns_sol; i++)
            for (int j = 0; j < num_dims; j++)
                ifs >> ins_clustering[i][j];
    }

    // 2. create the initial solutions
    if (!filename_ini.empty()) {
        ifstream ifs(filename_ini.c_str());
        for (int p = 0; p < pop_size; p++)
            for (int i = 0; i < num_patterns_sol; i++)
                ifs >> curr_pop[p][i];
    }
    else {
        for (int p = 0; p < pop_size; p++)
            for (int i = 0; i < num_patterns_sol; i++)
                curr_pop[p][i] = rand() % num_clusters;
    }
}

prega::obj_val_type prega::evaluate(const population& curr_pop)
{
    obj_val_type sse(pop_size, 0.0);

    for (int p = 0; p < pop_size; p++) {
        // 1. assign each pattern to its cluster
        vector<int> count_patterns(num_clusters, 0);
        for (int k = 0; k < num_clusters; k++)
            for (int d = 0; d < num_dims; d++)
                centroids[p][k][d] = 0.0;
        for (int k = 0; k < num_clusters; k++) {
            for (int i = 0; i < num_patterns_sol; i++) {
                if (curr_pop[p][i] == k) {
                    for (int d = 0; d < num_dims; d++)
                        centroids[p][k][d] += ins_clustering[i][d];
                    count_patterns[k]++;
                }
            }
        }

        // 2. compute the centroids (means)
        for (int k = 0; k < num_clusters; k++)
            for (int d = 0; d < num_dims; d++)
                centroids[p][k][d] /= count_patterns[k];

        // 3. compute sse
        for (int i = 0; i < num_patterns_sol; i++) {
            const int k = curr_pop[p][i];
            for (int d = 0; d < num_dims; d++)
                sse[p] += pow(ins_clustering[i][d] - centroids[p][k][d], 2);
        }
    }

    return sse;
}

prega::population prega::tournament_select(population& curr_pop, obj_val_type& curr_obj_vals, int num_players)
{
    population tmp_pop(curr_pop.size());
    pop_mask tmp_pr_mask(pop_size, sol_mask(num_patterns_sol, false));
    for (size_t i = 0; i < curr_pop.size(); i++) {
        int k = rand() % curr_pop.size();
        double f = curr_obj_vals[k];
        for (int j = 1; j < num_players; j++) {
            int n = rand() % curr_pop.size();
            if (curr_obj_vals[n] < f) {
                k = n;
                f = curr_obj_vals[k];
            }
        }
        tmp_pop[i] = curr_pop[k];
        tmp_pr_mask[i] = pr_mask[k];
    }
    pr_mask = tmp_pr_mask;
    return tmp_pop;
}

void prega::update_best_sol(const population& curr_pop, const obj_val_type& curr_obj_vals)
{
    for (size_t i = 0; i < curr_pop.size(); i++) {
        if (curr_obj_vals[i] < best_obj_val) {
            best_obj_val = curr_obj_vals[i];
            best_sol = curr_pop[i];
        }
    }
}

prega::population prega::crossover(population& curr_pop, double cr, pop_mask& pr_mask)  // one-point crossover
{
    const size_t mid = curr_pop.size()/2;
    for (size_t i = 0; i < mid; i++) {
        const double f = static_cast<double>(rand()) / RAND_MAX;
        if (f <= cr) {
            int xp = rand() % curr_pop[0].size();       // crossover point
            for (size_t j = xp; j < curr_pop[0].size(); j++) {
                if (!pr_mask[i][j])
                    swap(curr_pop[i][j], curr_pop[mid+i][j]);
            }
        }
    }
    return curr_pop;
}

prega::population prega::mutate(population& curr_pop, double mr, pop_mask& pr_mask)
{
    for (size_t i = 0; i < curr_pop.size(); i++) {
        const double f = static_cast<double>(rand()) / RAND_MAX;
        if (f <= mr) {
            const int m = rand() % curr_pop[0].size();  // mutation point
            if (!pr_mask[i][m])
                curr_pop[i][m] = rand() % num_clusters;
        }
    }
    return curr_pop;
}

prega::population prega::okm(population& curr_pop, pop_mask& pr_mask, int eval)
{
    for (size_t p = 0; p < curr_pop.size(); p++) {
        // 1. one iteration k-means
        vector<int> count(num_clusters, 0);
        for (int i = 0; i < num_patterns_sol; i++) {
            if (!pr_mask[p][i] || eval > num_evals/2) {
                double dist = numeric_limits<double>::max();
                int c = 0;
                for (int k = 0; k < num_clusters; k++) {
                    double dist_tmp = distance(ins_clustering[i], centroids[p][k]);
                    if (dist_tmp < dist) {
                        dist = dist_tmp;
                        c = k;
                    }
                }
                curr_pop[p][i] = c;
                ++count[c];
                if (centroid_dist[p][c] < dist)
                    centroid_dist[p][c] = dist;
            }
        }

        // 2. randomly assign a pattern to each empty cluster
        for (int k = 0; k < num_clusters; k++) {
            if (count[k] == 0) {
                const int i = rand() % num_patterns_sol;
                curr_pop[p][i] = k;
                if (pr_mask[p][i])
                    pr_mask[p][i] = false;
            }
        }
    }
    return curr_pop;
}

prega::pop_mask prega::detection(population& curr_pop, pop_mask& pr_mask, int eval)
{
    double rr = eval * reduction_rate;
    for (size_t p = 0; p < curr_pop.size(); p++) {
        vector<double> dist(num_clusters);
        for (int i = 0; i < num_clusters; i++)
            dist[i] = centroid_dist[p][i] * rr;
        for (int i = 0; i < num_patterns_sol; i++) {
            if (!pr_mask[p][i]) {
                double dist_tmp = distance(ins_clustering[i], centroids[p][curr_pop[p][i]]);
                if (dist_tmp < dist[curr_pop[p][i]])
                    pr_mask[p][i] = true;
            }
        }
    }
    return pr_mask;
}

void prega::redundant_analysis_1(const int curr_gen)
{
    pop_conv[curr_gen] = curr_pop;
}

void prega::redundant_analysis_2(const int curr_gen, const int curr_run)
{
    // 1. find the generation at which each subsolution reaches the final state for each run
    for (int i = 0; i < pop_size; i++) {
        for (int j = 0; j < num_patterns_sol; j++) {
            for (int k = curr_gen-1 ; k > 1 ; k--) {
                if (pop_conv[k][i][j] != pop_conv[k-1][i][j]) {
                    final_state[curr_run][i][j] = k;
                    break;
                }
            }
        }
    }

    // 2. accumulate the information obtained above for each run
    for (int k = 0 ; k < curr_gen ; k++) {
        int final_state_count = 0;
        for (int i = 0; i < pop_size; i++) {
            for (int j = 0; j < num_patterns_sol; j++) {
                if (final_state[curr_run][i][j] <= k)
                    final_state_count++;
            }
        }
        avg_final_state[curr_run][k] = final_state_count / pop_size;
        all_final_state[k] += avg_final_state[curr_run][k];
    }

    // 3. compute the percentage of subsolutions that reach the final state for all runs
    if (curr_run == num_runs-1) {
        cout << "rd: ";
        for (int k = 0 ; k < curr_gen ; k++)
            cout << fixed << setprecision(3) << all_final_state[k] / (num_runs * num_patterns_sol) << ", ";
        cout << endl;
    }
}

#endif
