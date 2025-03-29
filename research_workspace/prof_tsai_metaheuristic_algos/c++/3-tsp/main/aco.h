#ifndef __ACO_H_INCLUDED__
#define __ACO_H_INCLUDED__

#include <iostream>
#include <string>
#include <vector>
#include <fstream>
#include <list>
#include <limits>

using namespace std;

class aco
{
public:
    typedef vector<int> solution;
    typedef vector<solution> population;
    typedef vector<double> pattern;
    typedef vector<pattern> instance;
    typedef vector<double> pheromone_1d;
    typedef vector<pheromone_1d> pheromone_2d;
    typedef vector<double> dist_1d;
    typedef vector<dist_1d> dist_2d;
    typedef vector<double> obj_val_t;

    aco(int num_runs,
        int num_evals,
        int num_patterns_ins,
        string filename_ini,
        string filename_ins,
        int pop_size,
        double alpha,
        double beta,
        double rho,
        double q0);

    population run();

private:
    void init();
    void construct_solutions(population& curr_pop, const dist_2d& dist, pheromone_2d& ph, double beta, double q0);
    obj_val_t evaluate(const population& curr_pop);
    void update_global_ph(pheromone_2d& ph, const solution& best_sol, double best_obj_val);
    void update_local_ph(pheromone_2d& ph, int curr_city, int next_city);
    void update_best_sol(population& curr_pop, obj_val_t& curr_obj_vals);
    void show_optimum();

private:
    int num_runs;
    int num_evals;
    int num_patterns_sol;
    string filename_ini;
    string filename_ins;

    double avg_obj_val;
    vector<double> avg_obj_val_eval;
    double best_obj_val;
    solution best_sol;
    instance ins_tsp;
    solution opt_sol;

    // data members for population-based algorithms
    int pop_size;
    population curr_pop;
    population temp_pop;
    obj_val_t curr_obj_vals;

    // data member for aco-specific parameters
    double alpha;
    double beta;
    double rho;
    double q0;
    double tau0;
    pheromone_2d ph;
    pheromone_2d tau_eta;
    dist_2d dist;
};

inline aco::aco(int num_runs,
                int num_evals,
                int num_patterns_sol,
                string filename_ini,
                string filename_ins,
                int pop_size,
                double alpha,
                double beta,
                double rho,
                double q0
                )
    : num_runs(num_runs),
      num_evals(num_evals),
      num_patterns_sol(num_patterns_sol),
      filename_ini(filename_ini),
      filename_ins(filename_ins),
      pop_size(pop_size),
      alpha(alpha),
      beta(beta),
      rho(rho),
      q0(q0)
{
    srand();
}

inline aco::population aco::run()
{
    avg_obj_val = 0.0;
    obj_val_t avg_obj_val_eval(num_evals, 0.0);

    for (int r = 0; r < num_runs; r++) {
        int eval_count = 0;
        double best_so_far = numeric_limits<double>::max();

        // 0. initialization
        init();

        while (eval_count < num_evals) {
            // 1. transition
            construct_solutions(curr_pop, dist, ph, beta, q0);

            // 2. evaluation
            curr_obj_vals = evaluate(curr_pop);

            for (size_t i = 0; i < curr_obj_vals.size(); i++) {
                if (best_so_far > curr_obj_vals[i])
                    best_so_far = curr_obj_vals[i];
                if (eval_count < num_evals)
                    avg_obj_val_eval[eval_count++] += best_so_far;
            }

            // 3. determination
            update_best_sol(curr_pop, curr_obj_vals);
            update_global_ph(ph, best_sol, best_obj_val);
        }
        avg_obj_val += best_obj_val;
    }
    avg_obj_val /= num_runs;

    for (int i = 0; i < num_evals; i++) {
        avg_obj_val_eval[i] /= num_runs;
        cout << fixed << setprecision(3) << avg_obj_val_eval[i] << endl;
    }

    show_optimum();

    return curr_pop;
}

inline void aco::init()
{
    // 1. parameters initialization
    //
    // Well, some of them should be moved to the constructor because
    // they need to be initialized once and only once; some of them
    // should be declared and/or initialized where it is used.
    ins_tsp = instance(num_patterns_sol, pattern(2, 0.0));
    curr_pop = temp_pop = population(pop_size, solution(num_patterns_sol, 0));
    opt_sol = solution(num_patterns_sol, 0);
    ph = pheromone_2d(num_patterns_sol, pheromone_1d(num_patterns_sol, tau0));
    dist = dist_2d(num_patterns_sol, dist_1d(num_patterns_sol, 0.0));
    obj_val_t curr_obj_vals(pop_size, 0.0);
    solution best_sol(num_patterns_sol, 0);
    best_obj_val = numeric_limits<double>::max();

    // 2. input the TSP benchmark
    if (!filename_ins.empty()) {
        ifstream ifs(filename_ins.c_str());
        for (int i = 0; i < num_patterns_sol ; i++)
            ifs >> ins_tsp[i][0] >> ins_tsp[i][1];
    }

    // 3. input the optimum solution
    string filename_ins_opt(filename_ins + ".opt");
    if (!filename_ins_opt.empty()) {
        ifstream ifs(filename_ins_opt.c_str());
        for (int i = 0; i < num_patterns_sol ; i++) {
            ifs >> opt_sol[i];
            --opt_sol[i];
        }
    }

    // 4. initial solutions
    if (!filename_ini.empty()) {
        ifstream ifs(filename_ini.c_str());
        for (int k = 0; k < pop_size; k++)
            for (int i = 0; i < num_patterns_sol; i++)
                ifs >> curr_pop[k][i];
    }
    else {
        for (int k = 0; k < pop_size; k++) {
            for (int i = 0; i < num_patterns_sol; i++)
                curr_pop[k][i] = i;
            for (int i = num_patterns_sol-1; i > 0; --i)        // shuffle the solutions
                swap(curr_pop[k][i], curr_pop[k][rand() % (i+1)]);
        }
    }

    // 5. construct the distance matrix
    for (int i = 0; i < num_patterns_sol; i++) {
        ph[i][i] = 0.0;
        for (int j = 0; j < num_patterns_sol; j++)
            dist[i][j] = i == j ? 0.0 : distance(ins_tsp[i], ins_tsp[j]);
    }

    // 6. create the pheromone table, by first constructing a solution using the nearest neighbor method
    const int n = rand() % curr_pop.size();
    list<int> cities(curr_pop[n].begin(), curr_pop[n].end());
    best_sol[0] = *cities.begin();
    cities.erase(cities.begin());
    double Lnn = 0.0;
    for (int i = 1; i < num_patterns_sol; i++) {
        const int r = best_sol[i-1];
        auto min_s = cities.begin(); // simply choose a city
        double min_dist = numeric_limits<double>::max();
        for (auto it = cities.begin(); it != cities.end(); it++) {
            const int s = *it;
            if (dist[r][s] < min_dist) {
                min_dist = dist[r][s];
                min_s = it;
            }
        }
        const int s = *min_s;
        best_sol[i] = s;
        cities.erase(min_s);
        Lnn += dist[r][s];
    }
    const int r = best_sol[num_patterns_sol-1];
    const int s = best_sol[0];
    Lnn += dist[r][s];

    tau0 = 1 / (num_patterns_sol * Lnn);
    for (int r = 0; r < num_patterns_sol; r++)
        for (int s = 0; s < num_patterns_sol; s++)
            ph[r][s] = r == s ? 0.0 : tau0;
}

inline void aco::construct_solutions(population& curr_pop, const dist_2d& dist, pheromone_2d& ph, double beta, double q0)
{
    int num_patterns_sol = curr_pop[0].size();

    // 1. tau eta
    pheromone_2d tau_eta(num_patterns_sol, pheromone_1d(num_patterns_sol));
    for (int r = 0; r < num_patterns_sol; r++)
        for (int s = 0; s < num_patterns_sol; s++)
            tau_eta[r][s] = r == s ? 0.0 : ph[r][s] * pow(1.0 / dist[r][s], beta);

    // 2. construct the solution: first, the first city of the tour
    population temp_pop = curr_pop;
    for (size_t j = 0; j < curr_pop.size(); j++) {
        solution& asol = temp_pop[j];
        const int n = rand() % num_patterns_sol;
        curr_pop[j][0] = asol[n];
        asol.erase(asol.begin() + n);
    }

    // 3. then, the remaining cities of the tour
    for (int i = 1; i < num_patterns_sol; i++) {
        // for each step
        for (size_t j = 0; j < curr_pop.size(); j++) {
            // for each ant
            solution& asol = temp_pop[j];
            int r = curr_pop[j][i-1];
            int s = asol[0];
            int x = 0;
            const double q = static_cast<double>(rand()) / RAND_MAX;
            if (q <= q0) {
                // 3.1. exploitation
                double max_tau_eta = tau_eta[r][s];
                for (size_t k = 1; k < asol.size(); k++) {
                    if (tau_eta[r][asol[k]] > max_tau_eta) {
                        s = asol[k];
                        x = k;
                        max_tau_eta = tau_eta[r][s];
                    }
                }
            }
            else {
                // 3.2. biased exploration
                double total = 0.0;
                for (size_t k = 0; k < asol.size(); k++)
                    total += tau_eta[r][asol[k]];

                // 3.3. choose the next city based on the probability
                double f = total * static_cast<double>(rand()) / RAND_MAX;
                for (size_t k = 0; k < asol.size(); k++) {
                    if ((f -= tau_eta[r][asol[k]]) <= 0) {
                        s = asol[k];
                        x = k;
                        break;
                    }
                }
            }
            curr_pop[j][i] = s;
            asol.erase(asol.begin() + x);

            // 4.1. update local pheromones, 0 to n-1
            update_local_ph(ph, r, s);
        }
    }

    // 4.2. update local pheromones, n-1 to 0
    for (size_t k = 0; k < curr_pop.size(); k++) {
        // for each ant
        const int r = curr_pop[k][curr_pop[0].size()-1];
        const int s = curr_pop[k][0];
        update_local_ph(ph, r, s);
    }
}

inline aco::obj_val_t aco::evaluate(const population& curr_pop)
{
    obj_val_t tour_dist(curr_pop.size(), 0.0);
    for (size_t k = 0; k < curr_pop.size(); k++) {
        for (size_t i = 0; i < curr_pop[0].size(); i++) {
            const int r = curr_pop[k][i];
            const int s = curr_pop[k][(i+1) % curr_pop[0].size()];
            tour_dist[k] += dist[r][s];
        }
    }
    return tour_dist;
}

inline void aco::update_best_sol(population& curr_pop, obj_val_t& curr_obj_vals)
{
    for (size_t i = 0; i < curr_pop.size(); i++) {
        if (curr_obj_vals[i] < best_obj_val) {
            best_obj_val = curr_obj_vals[i];
            best_sol = curr_pop[i];
        }
    }
}

inline void aco::update_global_ph(pheromone_2d& ph, const solution& best_sol, double best_obj_val)
{
    for (size_t i = 0; i < best_sol.size(); i++) {
        const int r = best_sol[i];
        const int s = best_sol[(i+1) % best_sol.size()];
        ph[s][r] = ph[r][s] = (1 - alpha) * ph[r][s] + alpha * (1 / best_obj_val);
    }
}

inline void aco::update_local_ph(pheromone_2d& ph, int r, int s)
{
    ph[s][r] = ph[r][s] = (1 - rho) * ph[r][s] + rho * tau0;
}

inline void aco::show_optimum()
{
    double opt_dist = 0;
    for (int i = 0; i < num_patterns_sol; i++) {
        const int r = opt_sol[i];
        const int s = opt_sol[(i+1) % num_patterns_sol];
        opt_dist += dist[r][s];
    }
    cerr << "# Current route: " << best_sol << endl;
    cerr << "# Optimum distance: " << fixed << setprecision(3) << opt_dist << endl;
    cerr << "# Optimum route: " << opt_sol << endl;
}

#endif
