#include <iostream>
#include <iomanip>
#include <string>
#include <map>
#include <tuple>

using namespace std;

extern int main_hc(int argc, char** argv);
extern int main_sa(int argc, char** argv);
extern int main_sa_refinit(int argc, char** argv);
extern int main_ts(int argc, char** argv);
extern int main_hc_r(int argc, char** argv);
extern int main_ga(int argc, char** argv);
extern int main_gar(int argc, char** argv);
extern int main_gax2(int argc, char** argv);
extern int main_gaxu(int argc, char** argv);
extern int main_se(int argc, char** argv);

static map<const string, tuple<int(*)(int, char**), int, const char*>> dispatcher {
    {"hc",        {main_hc,          6, ""}},
    {"sa",        {main_sa,          8, "<min_temp> <max_temp>"}},
    {"sa_refinit",{main_sa_refinit, 10, "<min_temp> <max_temp> <#samples> <#same bits"}},
    {"ts",        {main_ts,          8, "<#neighbors> <tabulist_size>"}},
    {"hc_r",      {main_hc_r,        6, ""}},
    {"ga",        {main_ga,         10, "<popsize> <cr> <mr> <#players>"}},
    {"gar",       {main_gar,        10, "<popsize> <cr> <mr> <#players>"}},
    {"gax2",      {main_gax2,       10, "<popsize> <cr> <mr> <#players>"}},
    {"gaxu",      {main_gaxu,       10, "<popsize> <cr> <mr> <#players>"}},
    {"se",        {main_se,         11, "<#searchers> <#regions> <#samples> <#players> <scatter_plot?>"}},
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

    // now do and time the search
    const clock_t begin = clock();
    const int rc = get<0>(t)(argc, argv);
    const clock_t end = clock();

    const double cpu_time = static_cast<double>(end - begin) / CLOCKS_PER_SEC;
    cerr << "# CPU time used: " << cpu_time << " seconds." << endl;

    return rc;
}

#include "hc.h"
int main_hc(int argc, char** argv)
{
    hc hc_search(atoi(argv[2]),
                 atoi(argv[3]),
                 atoi(argv[4]),
                 argv[5]
                 );
    hc::solution s = hc_search.run();
    cerr << s << endl;
    return 0;
}

#include "sa.h"
int main_sa(int argc, char** argv)
{
    cerr << "# minimum temperature: " << argv[6] << endl
         << "# maximum temperature: " << argv[7] << endl;
    sa sa_search(atoi(argv[2]),
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

#include "sa_refinit.h"
int main_sa_refinit(int argc, char** argv)
{
    cerr << "# minimum temperature: " << argv[6] << endl
         << "# maximum temperature: " << argv[7] << endl
         << "# number of samplings: " << argv[8] << endl
         << "# number of same bits: " << argv[9] << endl;
    sa_refinit sa_refinit_search(atoi(argv[2]),
                                 atoi(argv[3]),
                                 atoi(argv[4]),
                                 argv[5],
                                 atof(argv[6]),
                                 atof(argv[7]),
                                 atoi(argv[8]),
                                 atoi(argv[9])
                                 );
    sa_refinit::solution s = sa_refinit_search.run();
    cerr << s << endl;
    return 0;
}

#include "ts.h"
int main_ts(int argc, char** argv)
{
    cerr << "# number of neighbors: " << argv[6] << endl
         << "# size of the tabu list: " << argv[7] << endl;
    ts ts_search(atoi(argv[2]),
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

#include "hc_r.h"
int main_hc_r(int argc, char** argv)
{
    hc_r hc_search(atoi(argv[2]),
                   atoi(argv[3]),
                   atoi(argv[4]),
                   argv[5]
                   );
    hc_r::solution s = hc_search.run();
    cerr << s << endl;
    return 0;
}

#include "ga.h"
int main_ga(int argc, char** argv)
{
    cerr << "# population size: " << argv[6] << endl
         << "# crossover rate: " << argv[7] << endl
         << "# mutation rate: " << argv[8] << endl
         << "# number of players: " << argv[9] << endl;
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

#include "gar.h"
int main_gar(int argc, char** argv)
{
    cerr << "# population size: " << argv[6] << endl
         << "# crossover rate: " << argv[7] << endl
         << "# mutation rate: " << argv[8] << endl
         << "# number of players: " << argv[9] << endl;
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

// two-point crossover
#include "gax2.h"
int main_gax2(int argc, char** argv)
{
    cerr << "# population size: " << argv[6] << endl
         << "# crossover rate: " << argv[7] << endl
         << "# mutation rate: " << argv[8] << endl
         << "# number of players: " << argv[9] << endl;
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

// uniform crossover
#include "gaxu.h"
int main_gaxu(int argc, char** argv)
{
    cerr << "# population size: " << argv[6] << endl
         << "# crossover rate: " << argv[7] << endl
         << "# mutation rate: " << argv[8] << endl
         << "# number of players: " << argv[9] << endl;
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

#include "se.h"
int main_se(int argc, char** argv)
{
    cerr << "# number of searchers: " << argv[6] << endl
         << "# number of regions: " << argv[7] << endl
         << "# number of samples: " << argv[8] << endl
         << "# number of players: " << argv[9] << endl
         << "# scatter plot?: " << argv[10] << endl;
    se se_search(atoi(argv[2]),
                 atoi(argv[3]),
                 atoi(argv[4]),
                 argv[5],
                 atoi(argv[6]),
                 atoi(argv[7]),
                 atoi(argv[8]),
                 atoi(argv[9]),
                 atoi(argv[10])
                 );
    se_search.run();
    return 0;
}
