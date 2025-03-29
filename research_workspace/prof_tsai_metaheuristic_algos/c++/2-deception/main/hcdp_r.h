#ifndef __HCDP_R_H_INCLUDED__
#define __HCDP_R_H_INCLUDED__

#include "hcdp.h"

class hcdp_r: public hcdp
{
public:
    using hcdp::hcdp;

private:
    solution transit(const solution& s) override
    {
        return ::transit_r(s);
    }
};

#endif
