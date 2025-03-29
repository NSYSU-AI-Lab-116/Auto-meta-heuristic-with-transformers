#ifndef __HCDP_H_INCLUDED__
#define __HCDP_H_INCLUDED__

#include "hc.h"

class hcdp: public hc
{
public:
    using hc::hc;

private:
    int evaluate(const solution& s) override;
};


inline int hcdp::evaluate(const solution& s)
{
    int n = 0;
    for (size_t i = 0; i < s.size(); i++)
        n += s[i] << ((s.size() - 1) - i);
    return abs(n - (1 << (s.size()-2)));
}

#endif
