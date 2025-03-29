#ifndef __HCDP_RM_H_INCLUDED__
#define __HCDP_RM_H_INCLUDED__

#include "hcdp_r.h"

class hcdp_rm: public hcdp_r
{
public:
    using hcdp_r::hcdp_r;

private:    
    void determine(const solution& v, int fv, solution& s, int &fs) override
    {
        if (fv >= fs) {
            fs = fv;
            s = v;
        }
    } 
};

#endif
