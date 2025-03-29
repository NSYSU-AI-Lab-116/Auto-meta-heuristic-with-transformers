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
extern int main_prega(int argc, char** argv);

static map<const string, tuple<int(*)(int, char**), int, const char*>> dispatcher {
    {"ga",     {main_ga,    14, "<popsize> <cr> <mr> <#players> <pra?>"}},
    {"prega",  {main_prega, 16, "<popsize> <cr> <mr> <#players> <#detections> <rr> <pra?>"}},
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
             << " <algname> <#runs> <#evals> <#patterns> <#dims> <#clusters>"
             << " <filename_ini> <filename_ins>"
             << " " << get<2>(t)
             << endl;
        return 1;
    }

    cerr << "# name of the search algorithm: '" << argv[1] << "'" << endl
         << "# number of runs: " << argv[2] << endl
         << "# number of evaluations: " << argv[3] << endl
         << "# number of patterns: " << argv[4] << endl
         << "# number of dimensions: " << argv[5] << endl
         << "# number of clusters: " << argv[6] << endl
         << "# filename of the initial seeds: '" << argv[7] << "'" << endl
         << "# filename of the data set to be clustered: '" << argv[8] << "'" << endl;

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
    cerr << "# population size: " << argv[9] << endl
         << "# crossover rate: " << argv[10] << endl
         << "# mutation rate: " << argv[11] << endl
         << "# number of players: " << argv[12] << endl
         << "# pra?: " << argv[13] << endl;
    ga ga_search(atoi(argv[2]),
                 atoi(argv[3]),
                 atoi(argv[4]),
                 atoi(argv[5]),
                 atoi(argv[6]),
                 argv[7],
                 argv[8],
                 atoi(argv[9]),
                 atof(argv[10]),
                 atof(argv[11]),
                 atoi(argv[12]),
                 atoi(argv[13]) // pra?
                 );
    ga::population p = ga_search.run();
    cout << p << endl;
    return 0;
}

#include "prega.h"
int main_prega(int argc, char** argv)
{
    cerr << "# population size: " << argv[9] << endl
         << "# crossover rate: " << argv[10] << endl
         << "# mutation rate: " << argv[11] << endl
         << "# number of players: " << argv[12] << endl
         << "# number of detections: " << argv[13] << endl
         << "# reduction rate: " << argv[14] << endl
         << "# pra?: " << argv[15] << endl;
    prega prega_search(atoi(argv[2]),
                       atoi(argv[3]),
                       atoi(argv[4]),
                       atoi(argv[5]),
                       atoi(argv[6]),
                       argv[7],
                       argv[8],
                       atoi(argv[9]),   // population size
                       atof(argv[10]),  // crossover rate
                       atof(argv[11]),  // mutation rate
                       atoi(argv[12]),
                       atoi(argv[13]),  // number of detections
                       atof(argv[14]),  // reduction rate
                       atoi(argv[15])   // pra?
                       );
    prega::population p = prega_search.run();
    cout << p << endl;
    return 0;
}
