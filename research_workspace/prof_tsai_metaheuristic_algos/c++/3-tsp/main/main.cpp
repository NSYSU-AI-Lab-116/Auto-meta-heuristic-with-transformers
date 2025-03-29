#include <iostream>
#include <iomanip>
#include <string>
#include <map>
#include <tuple>
#include <thread>
#include "lib.h"

using namespace std;

// things to do to add a new algorithm:
//
// 1. declare the main function for the new algorithm, say main_x
//    where x is the name of the algorithm, below.
//
// 2. add the new algorithm to the dispatcher by adding a new entry,
//    which includes in order (1) the name of the algorithm, (2) the
//    main function just declared, (3) the number of parameters
//    required, and (4) a string specifying the parameters specific to
//    this particular algorithm.
//
// 3. add the implementation of main_x at the end of the file.

extern int main_aco(int argc, char** argv);
extern int main_ga(int argc, char** argv);
extern int main_gapmx(int argc, char** argv);
extern int main_gacx(int argc, char** argv);
extern int main_gaox(int argc, char** argv);
extern int main_pga(int argc, char** argv);
extern int main_hga(int argc, char** argv);
extern int main_gals(int argc, char** argv);

static map<const string, tuple<int(*)(int, char**), int, const char*>> dispatcher {
    {"aco",   {main_aco,   12, "<popsize> <alpha> <beta> <rho> <Q>"}},
    {"ga",    {main_ga,    11, "<popsize> <cr> <mr> <#players>"}},
    {"gapmx", {main_gapmx, 11, "<popsize> <cr> <mr> <#players>"}},
    {"gacx",  {main_gacx,  11, "<popsize> <cr> <mr> <#players>"}},
    {"gaox",  {main_gaox,  11, "<popsize> <cr> <mr> <#players>"}},
    {"pga",   {main_pga,   12, "<popsize> <cr> <mr> <#players> <#sub_pops>"}},
    {"hga",   {main_hga,   15, "<popsize> <cr> <mr> <#players> <#evals_sa> <time2run> <max_temp_sa> <min_temp_sa>"}}, // need to check players
    {"gals",  {main_gals,  13, "<popsize> <cr> <mr> <#players> <#ls_per_eval> <ls sol?>"}},
};

int main(int argc, char** argv)
{
    if (argc < 2) {
        cerr << "# The name of algorithm is missing!" << endl;
        return 1;
    }

    const auto& iter = dispatcher.find(argv[1]);
    if (iter == dispatcher.end()) {
        cerr << "# The specified algorithm '" << argv[1] << "' is not found!" << endl;
        return 1;
    }

    const auto& t = iter->second;

    if (argc != get<1>(t)) {
        cerr << "Usage: ./search"
             << " <algname> <#runs> <#evals> <#patterns> <filename_ini> <filename_ins>"
             << " " << get<2>(t)
             << endl;
        return 1;
    }

    cerr << "# name of the search algorithm: '" << argv[1] << "'" << endl
         << "# number of runs: " << argv[2] << endl
         << "# number of evaluations: " << argv[3] << endl
         << "# number of patterns: " << argv[4] << endl
         << "# filename of the initial seeds: '" << argv[5] << "'" << endl
         << "# filename of the benchmark: '" << argv[6] << "'" << endl;

    // now do and time the search
    const clock_t begin = clock();
    const int rc = get<0>(t)(argc, argv);
    const clock_t end = clock();

    const double cpu_time = static_cast<double>(end - begin) / CLOCKS_PER_SEC;
    cerr << "# CPU time used: " << cpu_time << " seconds." << endl;

    return rc;
}

#include "aco.h"
int main_aco(int argc, char** argv)
{
    cerr << "# population size (i.e., number of ants): " << argv[7] << endl
         << "# alpha: " << argv[8] << endl
         << "# beta: " << argv[9] << endl
         << "# rho: " << argv[10] << endl
         << "# Q: " << argv[11] << endl;

    aco aco_search(atoi(argv[2]),
                   atoi(argv[3]),
                   atoi(argv[4]),
                   argv[5],
                   argv[6],
                   atoi(argv[7]),       // number of ants
                   atof(argv[8]),       // alpha
                   atof(argv[9]),       // beta
                   atof(argv[10]),      // rho
                   atof(argv[11]));     // Q
    aco::population p = aco_search.run();
    return 0;
}

#include "ga.h"
int main_ga(int argc, char** argv)
{
    cerr << "# population size: " << argv[7] << endl
         << "# crossover rate: " << argv[8] << endl
         << "# mutation rate: " << argv[9] << endl
         << "# number of players: " << argv[9] << endl;
    ga ga_search(atoi(argv[2]),
                 atoi(argv[3]),
                 atoi(argv[4]),
                 argv[5],
                 argv[6],
                 atoi(argv[7]),
                 atof(argv[8]),
                 atof(argv[9]),
                 atoi(argv[10])
                 );
    ga::population p = ga_search.run();
    return 0;
}

#include "gapmx.h"
int main_gapmx(int argc, char** argv)
{
    cerr << "# population size: " << argv[7] << endl
         << "# crossover rate: " << argv[8] << endl
         << "# mutation rate: " << argv[9] << endl
         << "# number of players: " << argv[10] << endl;
    gapmx ga_search(atoi(argv[2]),
                    atoi(argv[3]),
                    atoi(argv[4]),
                    argv[5],
                    argv[6],
                    atoi(argv[7]),
                    atof(argv[8]),
                    atof(argv[9]),
                    atoi(argv[10])
                    );
    ga::population p = ga_search.run();
    return 0;
}

#include "gacx.h"
int main_gacx(int argc, char** argv)
{
    cerr << "# population size: " << argv[7] << endl
         << "# crossover rate: " << argv[8] << endl
         << "# mutation rate: " << argv[9] << endl
         << "# number of players: " << argv[10] << endl;
    gacx ga_search(atoi(argv[2]),
                   atoi(argv[3]),
                   atoi(argv[4]),
                   argv[5],
                   argv[6],
                   atoi(argv[7]),
                   atof(argv[8]),
                   atof(argv[9]),
                   atoi(argv[10])
                   );
    ga::population p = ga_search.run();
    return 0;
}

#include "gaox.h"
int main_gaox(int argc, char** argv)
{
    cerr << "# population size: " << argv[7] << endl
         << "# crossover rate: " << argv[8] << endl
         << "# mutation rate: " << argv[9] << endl
         << "# number of players: " << argv[10] << endl;
    gaox ga_search(atoi(argv[2]),
                   atoi(argv[3]),
                   atoi(argv[4]),
                   argv[5],
                   argv[6],
                   atoi(argv[7]),
                   atof(argv[8]),
                   atof(argv[9]),
                   atoi(argv[10])
                   );
    ga::population p = ga_search.run();
    return 0;
}

#include "pga.h"
int main_pga(int argc, char** argv)
{
    cerr << "# population size: " << argv[7] << endl
         << "# crossover rate: " << argv[8] << endl
         << "# mutation rate: " << argv[9] << endl
         << "# number of players: " << argv[10] << endl
         << "# number of threads: " << argv[11] << endl;
    pga pga_search(atoi(argv[2]),
                   atoi(argv[3]),
                   atoi(argv[4]),
                   argv[5],
                   argv[6],
                   atoi(argv[7]),
                   atof(argv[8]),
                   atof(argv[9]),
                   atoi(argv[10]),
                   atoi(argv[11])
                   );
    pga::population p = pga_search.run();
    return 0;
}

#include "hga.h"
int main_hga(int argc, char** argv)
{
    cerr << "# population size: " << argv[7] << endl
         << "# crossover rate: " << argv[8] << endl
         << "# mutation rate: " << argv[9] << endl
         << "# number of players: " << argv[10] << endl
         << "# number of evaluations for SA: " << argv[11] << endl
         << "# run SA after n% of evaluations: " << argv[12] << endl
         << "# maximum temperature for SA: " << argv[13] << endl
         << "# minimum temperature for SA: " << argv[14] << endl;
    hga hga_search(atoi(argv[2]),
                   atoi(argv[3]),
                   atoi(argv[4]),
                   argv[5],
                   argv[6],
                   atoi(argv[7]),
                   atof(argv[8]),
                   atof(argv[9]),
                   atoi(argv[10]),
                   atoi(argv[11]),
                   atof(argv[12]),
                   atof(argv[13]),
                   atof(argv[14])
                   );
    hga::population p = hga_search.run();
    return 0;
}

#include "gals.h"
int main_gals(int argc, char** argv)
{
    cerr << "# population size: " << argv[7] << endl
         << "# crossover rate: " << argv[8] << endl
         << "# mutation rate: " << argv[9] << endl
         << "# number of players: " << argv[10] << endl
         << "# number of local searches per evaluation: " << argv[11] << endl
         << "# fine-tune? 0:population; 1:solution: " << argv[12] << endl;
    gals gals_search(atoi(argv[2]),
                     atoi(argv[3]),
                     atoi(argv[4]),
                     argv[5],
                     argv[6],
                     atoi(argv[7]),
                     atof(argv[8]),
                     atof(argv[9]),
                     atoi(argv[10]),
                     atoi(argv[11]),
                     atoi(argv[12])
                     );
    gals::population p = gals_search.run();
    return 0;
}
