#ifndef __SADP_H_INCLUDED__
#define __SADP_H_INCLUDED__

#include "sa.h"

class sadp: public sa
{
public:
    using sa::sa;

private:
    int evaluate(const solution& s) override;
};


inline int sadp::evaluate(const solution& s)
{
    int n = 0;
    for (size_t i = 0; i < s.size(); i++)
        n += s[i] << ((s.size() - 1) - i);
    return abs(n - (1 << (s.size()-2)));
}

#endif
