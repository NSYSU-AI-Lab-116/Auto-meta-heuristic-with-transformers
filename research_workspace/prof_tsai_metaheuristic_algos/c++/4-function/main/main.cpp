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

extern int main_pso(int argc, char** argv);
extern int main_de(int argc, char** argv);
extern int main_deb1(int argc, char** argv);
extern int main_decb1(int argc, char** argv);
extern int main_deb2(int argc, char** argv);
extern int main_der2(int argc, char** argv);

static map<const string, tuple<int(*)(int, char**), int, const char*>> dispatcher {
    {"pso",   {main_pso,   13, "<omega> <c1> <c2> <v_min> <v_max>"}},
    {"de",    {main_de,    12, "<F> <cr> <v_min> <v_max>"}},
    {"deb1",  {main_deb1,  12, "<F> <cr> <v_min> <v_max>"}},
    {"decb1", {main_decb1, 12, "<F> <cr> <v_min> <v_max>"}},
    {"deb2",  {main_deb2,  12, "<F> <cr> <v_min> <v_max>"}},
    {"der2",  {main_der2,  12, "<F> <cr> <v_min> <v_max>"}},
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
             << " <algname> <#runs> <#evals> <#dims> <filename_ini> <filename_ins>"
             << " " << get<2>(t)
             << endl;
        return 1;
    }

    cerr << "# name of the search algorithm: '" << argv[1] << "'" << endl
         << "# number of runs: " << argv[2] << endl
         << "# number of evaluations: " << argv[3] << endl
         << "# number of dimensions: " << argv[4] << endl
         << "# filename of the initial seeds: '" << argv[5] << "'" << endl
         << "# name of the tsp benchmark: '" << argv[6] << "'" << endl
         << "# population size: " << argv[7] << endl;

    const clock_t begin = clock();
    const int rc = get<0>(t)(argc, argv);
    const clock_t end = clock();

    const double cpu_time = static_cast<double>(end - begin) / CLOCKS_PER_SEC;
    cerr << "# CPU time used: " << cpu_time << " seconds." << endl;

    return rc;
}

#include "pso.h"
int main_pso(int argc, char** argv)
{
    cerr << "# omega: " << argv[8] << endl
         << "# c1: " << argv[9] << endl
         << "# c2: " << argv[10] << endl
         << "# v_min: " << argv[11] << endl
         << "# v_max: " << argv[12] << endl;

    pso pso_search(atoi(argv[2]),
                   atoi(argv[3]),
                   atoi(argv[4]),
                   argv[5],
                   argv[6],
                   atoi(argv[7]),
                   atof(argv[8]),       // omega
                   atof(argv[9]),       // c1
                   atof(argv[10]),      // c2
                   atof(argv[11]),      // v_min
                   atof(argv[12]));     // v_max
    pso::population ps = pso_search.run();

    return 0;
}

#include "de.h"
int main_de(int argc, char** argv)
{
    cerr << "# F: " << argv[8] << endl
         << "# cr: " << argv[9] << endl
         << "# v_min: " << argv[10] << endl
         << "# v_max: " << argv[11] << endl;

    de de_search(atoi(argv[2]),
                 atoi(argv[3]),
                 atoi(argv[4]),
                 argv[5],
                 argv[6],
                 atoi(argv[7]),
                 atof(argv[8]),         // scale factor F
                 atof(argv[9]),         // crossover rate cr
                 atof(argv[10]),        // v_min
                 atof(argv[11]));       // v_max

    de::population ps = de_search.run();

    return 0;
}

#include "deb1.h"
int main_deb1(int argc, char** argv)
{
    cerr << "# F: " << argv[8] << endl
         << "# cr: " << argv[9] << endl
         << "# v_min: " << argv[10] << endl
         << "# v_max: " << argv[11] << endl;

    deb1 deb1_search(atoi(argv[2]),
                     atoi(argv[3]),
                     atoi(argv[4]),
                     argv[5],
                     argv[6],
                     atoi(argv[7]),
                     atof(argv[8]),     // scale factor F
                     atof(argv[9]),     // crossover rate cr
                     atof(argv[10]),    // v_min
                     atof(argv[11]));   // v_max

    deb1::population ps = deb1_search.run();

    return 0;
}

#include "decb1.h"
int main_decb1(int argc, char** argv)
{
    cerr << "# F: " << argv[8] << endl
         << "# cr: " << argv[9] << endl
         << "# v_min: " << argv[10] << endl
         << "# v_max: " << argv[11] << endl;

    decb1 decb1_search(atoi(argv[2]),
                       atoi(argv[3]),
                       atoi(argv[4]),
                       argv[5],
                       argv[6],
                       atoi(argv[7]),
                       atof(argv[8]),   // scale factor F
                       atof(argv[9]),   // crossover rate cr
                       atof(argv[10]),  // v_min
                       atof(argv[11])); // v_max

    decb1::population ps = decb1_search.run();

    return 0;
}

#include "deb2.h"
int main_deb2(int argc, char** argv)
{
    cerr << "# F: " << argv[8] << endl
         << "# cr: " << argv[9] << endl
         << "# v_min: " << argv[10] << endl
         << "# v_max: " << argv[11] << endl;

    deb2 deb2_search(atoi(argv[2]),
                     atoi(argv[3]),
                     atoi(argv[4]),
                     argv[5],
                     argv[6],
                     atoi(argv[7]),
                     atof(argv[8]),     // scale factor F
                     atof(argv[9]),     // crossover rate cr
                     atof(argv[10]),    // v_min
                     atof(argv[11]));   // v_max

    deb2::population ps = deb2_search.run();

    return 0;
}

#include "der2.h"
int main_der2(int argc, char** argv)
{
    cerr << "# F: " << argv[8] << endl
         << "# cr: " << argv[9] << endl
         << "# v_min: " << argv[10] << endl
         << "# v_max: " << argv[11] << endl;

    der2 der2_search(atoi(argv[2]),
                     atoi(argv[3]),
                     atoi(argv[4]),
                     argv[5],
                     argv[6],
                     atoi(argv[7]),
                     atof(argv[8]),     // scale factor F
                     atof(argv[9]),     // crossover rate cr
                     atof(argv[10]),    // v_min
                     atof(argv[11]));   // v_max

    der2::population ps = der2_search.run();

    return 0;
}
