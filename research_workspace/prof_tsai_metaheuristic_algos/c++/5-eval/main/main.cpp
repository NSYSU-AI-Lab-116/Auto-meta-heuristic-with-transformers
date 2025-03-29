#include <iostream>
#include <iomanip>
#include <string>
#include <map>
#include <tuple>

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

extern int main_ga(int argc, char** argv);
extern int main_gax2(int argc, char** argv);
extern int main_gaxu(int argc, char** argv);
extern int main_gar(int argc, char** argv);
extern int main_garx2(int argc, char** argv);
extern int main_garxu(int argc, char** argv);

static map<const string, tuple<int(*)(int, char**), int, const char*>> dispatcher {
    {"ga",    {main_ga,   10, "<popsize> <cr> <mr> <#players>"}},
    {"gax2",  {main_gax2, 10, "<popsize> <cr> <mr> <#players>"}},
    {"gaxu",  {main_gaxu, 10, "<popsize> <cr> <mr> <#players>"}},
    {"gar",   {main_gar,  10, "<popsize> <cr> <mr> <#players>"}},
    {"garx2", {main_gax2, 10, "<popsize> <cr> <mr> <#players>"}},
    {"garxu", {main_gaxu, 10, "<popsize> <cr> <mr> <#players>"}},
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
             << " <algname> <#runs> <#evals> <#patterns> <filename_ini>"
             << " " << get<2>(t)
             << endl;
        return 1;
    }

    cerr << "# name of the search algorithm: '" << argv[1] << "'" << endl
         << "# number of runs: " << argv[2] << endl
         << "# number of evaluations: " << argv[3] << endl
         << "# number of patterns: " << argv[4] << endl
         << "# filename of the initial seeds: '" << argv[5] << "'" << endl
         << "# population size: " << argv[6] << endl
         << "# crossover rate: " << argv[7] << endl
         << "# mutation rate: " << argv[8] << endl
         << "# number of players: " << argv[9] << endl;

    // now do and time the search
    const clock_t begin = clock();
    const int rc = get<0>(t)(argc, argv);
    const clock_t end = clock();

    const double cpu_time = static_cast<double>(end - begin) / CLOCKS_PER_SEC;
    cerr << "# CPU time used: " << cpu_time << " seconds." << endl;

    return rc;
}

#include "ga.h"
int main_ga(int argc, char** argv)
{
    // one-point crossover
    ga ga_search(atoi(argv[2]),
                 atoi(argv[3]),
                 atoi(argv[4]),
                 argv[5],
                 atoi(argv[6]),
                 atof(argv[7]),
                 atof(argv[8]),
                 atoi(argv[9])
                 );
    ga::population p = ga_search.run();
    cerr << p << endl;
    return 0;
}

#include "gax2.h"
int main_gax2(int argc, char** argv)
{
    // two-point crossover
    gax2 gax2_search(atoi(argv[2]),
                     atoi(argv[3]),
                     atoi(argv[4]),
                     argv[5],
                     atoi(argv[6]),
                     atof(argv[7]),
                     atof(argv[8]),
                     atoi(argv[9])
                     );
    gax2::population p = gax2_search.run();
    cerr << p << endl;
    return 0;
}

#include "gaxu.h"
int main_gaxu(int argc, char** argv)
{
    // uniform crossover
    gaxu gaxu_search(atoi(argv[2]),
                     atoi(argv[3]),
                     atoi(argv[4]),
                     argv[5],
                     atoi(argv[6]),
                     atof(argv[7]),
                     atof(argv[8]),
                     atoi(argv[9])
                     );
    gaxu::population p = gaxu_search.run();
    cerr << p << endl;
    return 0;
}

#include "gar.h"
int main_gar(int argc, char** argv)
{
    cerr << "# population size: " << argv[6] << endl
         << "# crossover rate: " << argv[7] << endl
         << "# mutation rate: " << argv[8] << endl;
    gar gar_search(atoi(argv[2]),
                   atoi(argv[3]),
                   atoi(argv[4]),
                   argv[5],
                   atoi(argv[6]),
                   atof(argv[7]),
                   atof(argv[8]),
                   atoi(argv[9])
                   );
    gar::population p = gar_search.run();
    cerr << p << endl;
    return 0;
}

#include "garx2.h"
int main_garx2(int argc, char** argv)
{
    // two-point crossover
    garx2 garx2_search(atoi(argv[2]),
                       atoi(argv[3]),
                       atoi(argv[4]),
                       argv[5],
                       atoi(argv[6]),
                       atof(argv[7]),
                       atof(argv[8]),
                       atoi(argv[9])
                       );
    garx2::population p = garx2_search.run();
    cerr << p << endl;
    return 0;
}

#include "garxu.h"
int main_garxu(int argc, char** argv)
{
    // uniform crossover
    garxu garxu_search(atoi(argv[2]),
                       atoi(argv[3]),
                       atoi(argv[4]),
                       argv[5],
                       atoi(argv[6]),
                       atof(argv[7]),
                       atof(argv[8]),
                       atoi(argv[9])
                       );
    garxu::population p = garxu_search.run();
    cerr << p << endl;
    return 0;
}
