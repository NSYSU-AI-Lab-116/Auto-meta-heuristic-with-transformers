#ifndef __LIB_H_INCLUDED__
#define __LIB_H_INCLUDED__

#include <iostream>
#include <iomanip>
#include <vector>
#include <string>
#include <cmath>
#include <chrono>
#include <tuple>
#include <gmpxx.h>

using std::ostream;
using std::cerr;
using std::endl;
using std::fixed;
using std::setprecision;
using std::string;
using std::vector;
using std::tuple;
using std::make_tuple;
using std::tie;

using solution = vector<int>;
using population = vector<solution>;
using pheromone_1d = vector<double>;
using pheromone_2d = vector<pheromone_1d>;



inline ostream&
operator<<(ostream& os, const solution& s)
{
    os << "# " << s[0];
    for (size_t i = 1; i < s.size(); i++)
        os << ", " << s[i];
    return os;
}

inline ostream&
operator<<(ostream& os, const population& p)
{
    for (size_t i = 0; i < p.size()-1; i++)
        os << p[i] << endl;
    os << p[p.size()-1];
    return os;
}

inline ostream&
operator<<(ostream& os, const pheromone_1d& p)
{
    os << "# " << p[0];
    for (size_t i = 1; i < p.size(); i++)
        os << ", " << p[i];
    return os;
}

inline ostream&
operator<<(ostream& os, const pheromone_2d& p)
{
    for (size_t i = 0; i < p.size()-1; i++)
        os << p[i] << endl;
    os << p[p.size()-1];
    return os;
}

inline double
distance(const vector<double>& a, const vector<double>& b)
{
    double d = 0;
    for (size_t i = 0; i < a.size(); i++)
        d += (a[i]-b[i]) * (a[i]-b[i]);
    return sqrt(d);
}

inline solution
transit(const solution& s)
{
    string is(s.size(), '0');
    transform(s.begin(), s.end(), is.begin(), [] (int i) { return i + '0'; });
    const double r = static_cast<double>(rand()) / RAND_MAX;
    const mpz_class v = mpz_class(is, 2) + (r < 0.5 ? 1 : -1);
    if (v < 0 || v > (mpz_class(1) << s.size()) - 1)
        return s;
    string t = v.get_str(2);
    t.insert(0, s.size() - t.size(), '0');;
    vector<int> os(s.size(), 0);
    transform(t.begin(), t.end(), os.begin(), [] (int i) { return i - '0'; });
    return os;
}

inline solution
transit_r(const solution& s)
{
    solution t(s);
    const int i = rand() % t.size();
    t[i] = !t[i];
    return t;
}

inline void
srand()
{
    unsigned int seed = std::chrono::system_clock::now().time_since_epoch().count();
    cerr << "# seed: " << seed << endl;
    srand(seed);
}

#endif
