#ifndef __HC_R_H_INCLUDED__
#define __HC_R_H_INCLUDED__

#include "hc.h"

class hc_r: public hc
{
public:
    using hc::hc;

private:
    solution transit(const solution& s) override
    {
        return ::transit_r(s);
    }
};

#endif
