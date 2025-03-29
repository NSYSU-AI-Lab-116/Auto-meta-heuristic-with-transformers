#!/usr/bin/env python
import time; import sys; import os

ac = lambda: len(sys.argv)
si = lambda i: int(sys.argv[i])
sf = lambda i: float(sys.argv[i])
ss = lambda i: sys.argv[i]

_progname = os.path.basename(sys.argv[0])
_algname = _progname.split('.')[0]

class lib:
    @staticmethod
    def print_solution(sol, *, prefix = '# '):
        print(prefix, end='')
        print(*sol, sep=', ')

    @staticmethod
    def print_population(pop):
        for sol in pop:
            lib.print_solution(sol)

    @staticmethod
    def printf(fmt, *values):
        print(fmt % values)

    @staticmethod
    def usage(extra_params, *, common_params = "<#runs> <#evals> <#patterns> <filename_ini>"):
        if len(common_params) == 0:
            print("Usage: python %s %s" % (_progname, extra_params))
        else:
            print("Usage: python %s %s %s" % (_progname, common_params, extra_params))
        sys.exit(1)

    @staticmethod
    def run(search, print_result = print_solution):
        search.print_parameters(_algname)
        begin = time.time()
        res = search.run()
        if print_result is not None and res is not None:
            print_result(res)
        end = time.time()
        print("# CPU time used: %.6f seconds." % (end - begin))

if __name__ == "__main__":
    pass
