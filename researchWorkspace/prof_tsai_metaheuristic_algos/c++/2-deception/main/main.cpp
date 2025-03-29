#include <iostream>
#include <iomanip>
#include <string>
#include <map>
#include <tuple>

using std::cout;
using std::cerr;
using std::endl;
using std::string;
using std::map;
using std::tuple;
using std::get;

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

extern int main_hcdp(int argc, char** argv);
extern int main_hcdp_r(int argc, char** argv);
extern int main_hcdp_rm(int argc, char** argv);
extern int main_sadp(int argc, char** argv);
extern int main_tsdp(int argc, char** argv);
extern int main_gadp(int argc, char** argv);
extern int main_gardp(int argc, char** argv);

static map<const string, tuple<int(*)(int, char**), int, const char*>> dispatcher {
    {"hcdp",    {main_hcdp,    6, ""}},
    {"hcdp_r",  {main_hcdp_r,  6, ""}},
    {"hcdp_rm", {main_hcdp_rm, 6, ""}},
    {"sadp",    {main_sadp,    8, "<min_temp> <max_temp>"}},
    {"tsdp",    {main_tsdp,    8, "<#neighbors> <tabulistsize>"}},
    {"gadp",    {main_gadp,   10, "<popsize> <cr> <mr> <#players>"}},
    {"gardp",   {main_gardp,  10, "<popsize> <cr> <mr> <#players>"}},
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
         << "# filename of the initial seeds: '" << argv[5] << "'" << endl;


    const clock_t begin = clock();
    const int rc = get<0>(t)(argc, argv);
    const clock_t end = clock();

    const double cpu_time = static_cast<double>(end - begin) / CLOCKS_PER_SEC;
    cerr << "# CPU time used: " << cpu_time << " seconds." << endl;

    return rc;
}

#include "hcdp.h"
int main_hcdp(int argc, char** argv)
{
    hcdp hc_search(atoi(argv[2]),
                   atoi(argv[3]),
                   atoi(argv[4]),
                   argv[5]
                   );
    hc::solution s = hc_search.run();
    cerr << s << endl;
    return 0;
}

#include "hcdp_r.h"
int main_hcdp_r(int argc, char** argv)
{
    hcdp_r hc_search(atoi(argv[2]),
                     atoi(argv[3]),
                     atoi(argv[4]),
                     argv[5]
                     );
    hc::solution s = hc_search.run();
    cerr << s << endl;
    return 0;
}

#include "hcdp_rm.h"
int main_hcdp_rm(int argc, char** argv)
{
    hcdp_rm hc_search(atoi(argv[2]),
                      atoi(argv[3]),
                      atoi(argv[4]),
                      argv[5]
                      );
    hc::solution s = hc_search.run();
    cerr << s << endl;
    return 0;
}

#include "sadp.h"
int main_sadp(int argc, char** argv)
{
    cerr << "# minimum temperature: " << argv[6] << endl
         << "# maximum temperature: " << argv[7] << endl;
    sadp sa_search(atoi(argv[2]),
                   atoi(argv[3]),
                   atoi(argv[4]),
                   argv[5],
                   atof(argv[6]),
                   atof(argv[7])
                   );
    sa::solution s = sa_search.run();
    cerr << s << endl;
    return 0;
}

#include "tsdp.h"
int main_tsdp(int argc, char** argv)
{
    cerr << "# number of neighbors: " << argv[6] << endl
         << "# size of the tabu list: " << argv[7] << endl;
    tsdp ts_search(atoi(argv[2]),
                   atoi(argv[3]),
                   atoi(argv[4]),
                   argv[5],
                   atoi(argv[6]),
                   atoi(argv[7])
                   );
    ts::solution s = ts_search.run();
    cerr << s << endl;
    return 0;
}

#include "gadp.h"
int main_gadp(int argc, char** argv)
{
    cerr << "# population size: " << argv[6] << endl
         << "# crossover rate: " << argv[7] << endl
         << "# mutation rate: " << argv[8] << endl
         << "# number of players: " << argv[9] << endl;
    gadp ga_search(atoi(argv[2]),
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

#include "gardp.h"
int main_gardp(int argc, char** argv)
{
    cerr << "# population size: " << argv[6] << endl
         << "# crossover rate: " << argv[7] << endl
         << "# mutation rate: " << argv[8] << endl
         << "# number of players: " << argv[9] << endl;
    gadp gar_search(atoi(argv[2]),
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
