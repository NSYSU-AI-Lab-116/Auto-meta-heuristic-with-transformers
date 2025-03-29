#include <iostream>
#include <string>
#include <cstdlib>
#include <gmpxx.h>

using namespace std;

using solution = string;

extern int es_search(int numbits);

static inline solution transit(const solution& s);
static inline int evaluate(const solution& s);
static inline void determine(int f, const solution&s, int& fbest, solution& sbest);

int
es_search(int numbits)
{
    // 0. initialization
    int fs = 0;
    solution s(numbits, '0');
    // 1. transition
    solution v = s;
    cout << fs << " # " << v << endl;
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
    mpz_class a = mpz_class(s, 2) + 1;
    if (a < 0 || a > (mpz_class(1) << s.size()) - 1)
        return string();
    string os = a.get_str(2);
    os.insert(0, s.size() - os.size(), '0');;
    return os;
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



int main(int argc, char *argv[])
{
    if (argc != 2 || atoi(argv[1]) <= 0) {
        cerr << "Usage: ./es <numbits> where <numbits> is a positive integer." << endl;
        return 1;
    }

    const int numbits = atoi(argv[1]);

    cerr << "# number of bits: " << numbits << endl;

    const clock_t begin = clock();
    const int rc = es_search(numbits);
    const clock_t end = clock();

    const double cpu_time = static_cast<double>(end - begin) / CLOCKS_PER_SEC;
    cerr << "# CPU time used: " << cpu_time << " seconds." << endl;

    return rc;
}
