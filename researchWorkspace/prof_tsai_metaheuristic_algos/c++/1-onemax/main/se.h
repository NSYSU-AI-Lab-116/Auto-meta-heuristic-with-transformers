#include <iostream>
#include <ctime>
#include <cmath>
#include <vector>

using namespace std;

class se {
public:
    typedef vector<int> i1d;
    typedef vector<i1d> i2d;
    typedef vector<i2d> i3d;
    typedef vector<i3d> i4d;
    typedef vector<double> d1d;
    typedef vector<d1d> d2d;
    typedef vector<d2d> d3d;

public:
    se(int num_runs,
       int num_evals,
       int num_bits_sol,
       string filename_ini,
       int num_searchers,
       int num_regions,
       int num_samples,
       int num_players,
       int scatter_plot
       );

    void run();

private:
    // 1. initialization
    void init();

    // 2. resource arrangement
    void resource_arrangement();

    // 3. vision search
    void vision_search(int eval);
    void transit();
    virtual void compute_expected_value(int eval);
    int  evaluate_fitness(const i1d& sol);
    void vision_selection(int player, int eval);

    // 4. marketing survey
    void marketing_survey(int& best_so_far);

private:
    // 0.1 environment settings
    int num_runs;
    int num_evals;
    int num_bits_sol;
    string filename_ini;
    int num_searchers;
    int num_regions;
    int num_samples;
    int num_players;
    int scatter_plot;

    // 0.2 search results
    d1d avg_obj_val_eval;
    int best_so_far;
    i1d best_sol;

    // 0.3 search algorithm
    i2d searcher_sol;       // [searcher, num_bits_sol]
    i3d sample_sol;         // [region, sample, num_bits_sol]
    i2d sample_sol_best;    // [region, num_bits_sol]
    i4d sampleV_sol;        // [searcher, region, sample, num_bits_sol]

    d1d searcher_sol_fitness;
    d2d sample_sol_fitness;
    d1d sample_sol_best_fitness;
    d3d sampleV_sol_fitness;

    d1d ta;
    d1d tb;

    d2d expected_value;
    d1d T_j;
    d1d M_j;

    i1d searcher_region_id; // [searcher], region to which a searcher is assigned
    i2d id_bits;            // region id: tabu bits
    int num_id_bits;        // number of tabu bits

    int eval_count;         // evaluation count
};

inline se::se(int num_runs,
              int num_evals,
              int num_bits_sol,
              string filename_ini,
              int num_searchers,
              int num_regions,
              int num_samples,
              int num_players,
              int scatter_plot
              )
    : num_runs(num_runs),
      num_evals(num_evals),
      num_bits_sol(num_bits_sol),
      filename_ini(filename_ini),
      num_searchers(num_searchers),
      num_regions(num_regions),
      num_samples(num_samples),
      num_players(num_players),
      scatter_plot(scatter_plot)
{
    srand();
}

inline void se::run()
{
    avg_obj_val_eval.assign(num_evals, 0.0);

    for (int r = 0; r < num_runs; r++) {
        init();                            // 1. initialization
        resource_arrangement();            // 2. resource arrangement
        while (eval_count < num_evals) {
            int eval_cc = eval_count;
            vision_search(eval_cc);        // 3. vision search
            marketing_survey(best_so_far); // 4. marketing survey
            for (int i = eval_cc; i < min(eval_count, num_evals); i++)
                avg_obj_val_eval[i] += best_so_far;
        }
    }

    cout << fixed << setprecision(3);
    for (int i = 0; i < num_evals; i++)
        cout << avg_obj_val_eval[i] / num_runs << endl;
}

// 1. initialization
inline void se::init()
{
    // set aside arrays for searchers, samples, and sampleV
    searcher_sol.assign(num_searchers, i1d(num_bits_sol, 0));
    sample_sol.assign(num_regions, i2d(num_samples, i1d(num_bits_sol, 0)));
    sample_sol_best.assign(num_regions, i1d(num_bits_sol, 0));
    sampleV_sol.assign(num_searchers, i3d(num_regions, i2d(num_samples*2, i1d(num_bits_sol, 0))));

    searcher_sol_fitness.assign(num_searchers, 0.0);
    sample_sol_fitness.assign(num_regions, d1d(num_samples, 0.0));
    sample_sol_best_fitness.assign(num_regions, 0.0);
    sampleV_sol_fitness.assign(num_searchers, d2d(num_regions, d1d(num_samples*2, 0.0)));

    best_sol.assign(num_bits_sol, 0);
    best_so_far = 0;
    eval_count = 0;

    for (int i = 0; i < num_searchers; i++)
        for (int j = 0; j < num_bits_sol; j++)
            searcher_sol[i][j] = rand() % 2;
}

// 2. resource arrangement
inline void se::resource_arrangement()
{
    // 2.1. initialize searchers and regions
    num_id_bits = log2(num_regions);
    searcher_region_id.assign(num_searchers, 0);
    id_bits.assign(num_regions, i1d(num_id_bits, 0));
    // region_id_bits();
    for (int i = 0; i < num_regions; i++) {
        int n = i;
        int j = num_id_bits;
        while (n > 0) {
            id_bits[i][--j] = n % 2;
            n /= 2;
        }
    }

    // 2.1.1 assign searchers to regions
    for (int i = 0; i < num_searchers; i++) {
        // assign_search_region(i, i % num_regions);
        const int r = i % num_regions;
        searcher_region_id[i] = r;
        for (int j = 0; j < num_id_bits; j++)
            searcher_sol[i][j] = id_bits[r][j];
    }

    // 2.1.2 initialize sample solutions
    for (int i = 0; i < num_regions; i++)
        for (int j = 0; j < num_samples; j++) {
            for (int k = 0; k < num_id_bits; k++)
                sample_sol[i][j][k] = id_bits[i][k];
            for (int k = num_id_bits; k < num_bits_sol; k++)
                sample_sol[i][j][k] = rand() % 2;
        }

    // 2.2. initialize investment and how long regions have not been searched
    ta.assign(num_regions, 0.0);
    tb.assign(num_regions, 1.0);
    for (int i = 0; i < num_searchers; i++) {
        int r = searcher_region_id[i];
        ta[r]++;
        tb[r] = 1.0;
    }

    // 2.3. initialize expected values (ev)
    expected_value.assign(num_searchers, d1d(num_regions, 0.0));
    T_j.assign(num_regions, 0.0);
    M_j.assign(num_regions, 0.0);
}

// 3. vision search
inline void se::vision_search(int eval)
{
    // 3.1 construct V (searcher X sample)
    if (eval > 0) transit();

    // 3.2 compute the expected value of all regions of searchers
    compute_expected_value(eval);

    // 3.3 select region to which a searcher will be assigned
    vision_selection(num_players, eval);
}

// 3.1 construct V (searcher X sample)
inline void se::transit()
{
    // 3.1.1 exchange information between searchers and samples;
    for (int i = 0; i < num_searchers; i++) {
        for (int j = 0; j < num_regions; j++) {
            for (int k = 0; k < num_samples; k++) {
                const int x = rand() % (num_bits_sol + 1);
                const int m = k << 1;

                for (int l = 0; l < num_id_bits; l++) {
                    sampleV_sol[i][j][m][l] = id_bits[j][l];
                    sampleV_sol[i][j][m+1][l] = id_bits[j][l];
                }

                for (int l = num_id_bits; l < num_bits_sol; l++) {
                    if (l < x) {
                        sampleV_sol[i][j][m][l] = searcher_sol[i][l];
                        sampleV_sol[i][j][m+1][l] = sample_sol[j][k][l];
                    }
                    else {
                        sampleV_sol[i][j][m][l] = sample_sol[j][k][l];
                        sampleV_sol[i][j][m+1][l] = searcher_sol[i][l];
                    }
                }
            }
        }
    }

    // 3.1.2 randomly change one bit of each solution in sampleV_sol
    for (int i = 0; i < num_searchers; i++) {
        for (int j = 0; j < num_regions; j++) {
            for (int k = 0; k < 2*num_samples; k++) {
                int m = rand() % num_bits_sol; // bit to mutate
                if (m >= num_id_bits)
                    sampleV_sol[i][j][k][m] = !sampleV_sol[i][j][k][m];
            }
        }
    }
}

// 3.2 expected value for onemax problem
inline void se::compute_expected_value(int eval)
{
    // 3.2.1 fitness value of searchers and sampleV_sol (new candidate solutions)
    if (eval == 0) {
        // 3.2.1a fitness value of searchers
        for (int i = 0; i < num_searchers; i++)
            searcher_sol_fitness[i] = evaluate_fitness(searcher_sol[i]);
    }
    else {
        // 3.2.1b fitness value of sampleV_sol (new candidate solutions)
        for (int i = 0; i < num_searchers; i++) {
            int j = searcher_region_id[i];
            if (scatter_plot == 1)
                cout << eval_count << " " << j-0.1*i+0.1*num_regions/2 << " " << i << " ";
            for (int k = 0; k < num_samples; k++) {
                int n = rand() % 2*num_samples;
                int f = evaluate_fitness(sampleV_sol[i][j][n]);

                if (f > searcher_sol_fitness[i]) {
                    searcher_sol[i] = sampleV_sol[i][j][n];
                    searcher_sol_fitness[i] = f;
                }

                if (f > sample_sol_fitness[j][k]) {
                    sample_sol[j][k] = sampleV_sol[i][j][n];
                    sample_sol_fitness[j][k] = f;
                }
            }
        }
        if (scatter_plot == 1)
            cout << endl;
    }

    // 3.2.2 fitness value of samples
    if (eval == 0) //
        for (int j = 0; j < num_regions; j++)
            for (int k = 0; k < num_samples; k++)
                sample_sol_fitness[j][k] = evaluate_fitness(sample_sol[j][k]);

    double total_sample_fitness = 0.0; // f(m_j)
    for (int j = 0; j < num_regions; j++) {
        double rbj = 0.0;
        int b = -1;

        for (int k = 0; k < num_samples; k++) {
            total_sample_fitness += sample_sol_fitness[j][k];
            // update fbj
            if (sample_sol_fitness[j][k] > rbj) {
                b = k;
                rbj = sample_sol_fitness[j][k];
            }
        }
        if (b >= 0) {
            sample_sol_best_fitness[j] = rbj;
            sample_sol_best[j] = sample_sol[j][b];
        }
    }

    // 3.2.3 M_j
    for (int j = 0; j < num_regions; j++)
        M_j[j] = sample_sol_best_fitness[j] / total_sample_fitness;

    // 3.2.4 T_j
    for (int j = 0; j < num_regions; j++)
        T_j[j] = ta[j] / tb[j];

    // 3.2.5 compute the expected_value
    for (int i = 0; i < num_searchers; i++) {
        for (int j = 0; j < num_regions; j++)
            expected_value[i][j] = T_j[j] * M_j[j];
    }
}

// subfunction: 3.2.1 fitness value
inline int se::evaluate_fitness(const i1d& sol)
{
    eval_count++;
    return accumulate(sol.begin(), sol.end(), 0);
}

// 3.3 select region to which a searcher will be assigned
inline void se::vision_selection(int player, int eval)
{
    for (int j = 0; j < num_regions; j++)
        tb[j]++;

    // find index of the best vij
    for (int i = 0; i < num_searchers; i++) {
        int j = rand() % num_regions;
        double ev = expected_value[i][j];
        for (int p = 0; p < num_players-1; p++) {
            int c = rand() % num_regions;
            if (expected_value[i][c] > ev) {
                j = c;
                ev = expected_value[i][j];
            }
        }

        // assign searcher i to region j
        searcher_region_id[i] = j;

        // update ta[j] and tb[j];
        ta[j]++;
        tb[j] = 1;
    }
}

// 4. marketing survey
inline void se::marketing_survey(int& best_so_far)
{
    for (int j = 0; j < num_regions; j++)
        if (tb[j] > 1)
            ta[j] = 1.0;

    for (int i = 0; i < num_searchers; i++)
        if (searcher_sol_fitness[i] > best_so_far) {
            best_so_far = searcher_sol_fitness[i];
            best_sol = searcher_sol[i];
        }

    for (int j = 0; j < num_regions; j++)
        for (int k = 0; k < num_samples; k++)
            if (sample_sol_fitness[j][k] > best_so_far) {
                best_so_far = sample_sol_fitness[j][k];
                best_sol = sample_sol[j][k];
            }
}
