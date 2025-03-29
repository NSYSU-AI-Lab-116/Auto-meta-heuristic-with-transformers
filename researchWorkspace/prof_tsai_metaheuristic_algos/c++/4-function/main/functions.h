#ifndef __FUNCTIONS_H_INCLUDED__
#define __FUNCTIONS_H_INCLUDED__

#include <map>
#include <string>
#include <vector>
#include <cmath>

using namespace std;

static constexpr auto pi = acos(-1);

inline double mvfAckley(int n, const vector<double>& x)
{
    double s1 = 0.0;
    double s2 = 0.0;
    for (int i = 0; i < n; i++) {
        s1 += x[i] * x[i];
        s2 += cos(2.0 * pi * x[i]);
    }
    return -20.0 * exp(-0.2 * sqrt(s1/n)) + 20.0 - exp(s2/n) + exp(1.0);
}

// here is the table for all the functions
map<const string, double(*)(int, const vector<double>&)> function_table {
    {"mvfAckley", mvfAckley}
};

#endif
