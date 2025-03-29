#include <iostream>
#include <string>
#include <gmpxx.h>
#include "es_search.h"

using std::cout;
using std::cerr;
using std::endl;
using std::string;

using solution = string;

static inline solution transit(const solution& s);
static inline int evaluate(const solution& s);
static inline void determine(int fv, const solution& v, int& fs, solution& s);

int
es_search(int n)
{
    // 0. initialization
    solution s(n, '0');
    int fs = evaluate(s);
    cout << fs << " # " << s << endl;
    // 1. transition
    solution v = s;
    while ((v = transit(v)).size() != 0) {
        // 2. evaluation
        int fv = evaluate(v);
        // 3. determination
        determine(fv, v, fs, s);
        cout << fs << " # " << v << endl;
    }
    cerr << "# " << fs << endl;
    return 0;
}

static inline string
transit(const string& s)
{
    mpz_class v = mpz_class(s, 2) + 1;
    if (v < 0 || v > (mpz_class(1) << s.size()) - 1)
        return string();
    string t = v.get_str(2);
    t.insert(0, s.size() - t.size(), '0');
    return t;
}

static inline int
evaluate(const solution &s)
{
    return count(s.begin(), s.end(), '1');
}

static inline void
determine(int fv, const solution& v, int& fs, solution& s)
{
    if (fv > fs) {
        fs = fv;
        s = v;
    }
}
