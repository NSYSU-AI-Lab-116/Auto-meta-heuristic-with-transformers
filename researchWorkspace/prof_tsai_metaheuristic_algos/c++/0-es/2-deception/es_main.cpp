#include <iostream>
#include <ctime>
#include "es_search.h"

using std::cerr;
using std::endl;
using std::atoi;
using std::clock;

int main(int argc, char *argv[])
{
    if (argc != 2 || atoi(argv[1]) <= 0) {
        cerr << "Usage: ./es <n> where <n> is a positive integer." << endl;
        return 1;
    }

    const int n = atoi(argv[1]);

    cerr << "# number of bits: " << n << endl;

    const clock_t begin = clock();
    const int rc = es_search(n);
    const clock_t end = clock();

    const double cpu_time = static_cast<double>(end - begin) / CLOCKS_PER_SEC;
    cerr << "# CPU time used: " << cpu_time << " seconds." << endl;

    return rc;
}
