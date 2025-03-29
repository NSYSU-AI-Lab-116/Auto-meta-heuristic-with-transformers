#!/usr/bin/env bash

set -x

source search.conf

(time ./0-es/1-onemax/es 10)                       >0-es/1-onemax/result/result-es-om-10.txt 2>&1
(time ./0-es/2-deception/es 4)                     >0-es/2-deception/result/result-es-deception-4.txt 2>&1
(time ./0-es/2-deception/es 10)                    >0-es/2-deception/result/result-es-deception-10.txt 2>&1

(time ./1-onemax/search hc         100 1000 10 "") >1-onemax/result/result-hc-om-lr-10-new.txt 2>&1
(time ./1-onemax/search hc_r       100 1000 10 "") >1-onemax/result/result-hc-om-random-10.txt 2>&1

(time ./2-deception/search hcdp    100 1000  4 "") >2-deception/result/result-hcdp-deception-lr-4.txt 2>&1
(time ./2-deception/search hcdp_r  100 1000  4 "") >2-deception/result/result-hcdp-deception-random-4-new.txt 2>&1
(time ./2-deception/search hcdp_rm 100 1000  4 "") >2-deception/result/result-hcdp-deception-random-m-4-new.txt 2>&1
(time ./2-deception/search hcdp    100 1000 10 "") >2-deception/result/result-hcdp-deception-lr-10.txt 2>&1
(time ./2-deception/search hcdp_r  100 1000 10 "") >2-deception/result/result-hcdp-deception-random-10-new.txt 2>&1
(time ./2-deception/search hcdp_rm 100 1000 10 "") >2-deception/result/result-hcdp-deception-random-m-10-new.txt 2>&1

set +x
