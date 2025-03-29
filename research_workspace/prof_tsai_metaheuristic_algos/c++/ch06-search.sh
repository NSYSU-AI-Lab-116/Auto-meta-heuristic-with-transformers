#!/usr/bin/env bash

set -x

source search.conf

(time ./1-onemax/search ts       100 1000     10 "" 3 7) >1-onemax/result/result-ts-om-10.txt 2>&1
(time ./1-onemax/search ts       100 1000     20 "" 3 7) >1-onemax/result/result-ts-om-20.txt 2>&1
(time ./1-onemax/search ts       100 1000     40 "" 3 7) >1-onemax/result/result-ts-om-40.txt 2>&1
(time ./1-onemax/search ts       100 1000     60 "" 3 7) >1-onemax/result/result-ts-om-60.txt 2>&1
(time ./1-onemax/search ts       100 1000     80 "" 3 7) >1-onemax/result/result-ts-om-80.txt 2>&1
(time ./1-onemax/search ts       100 1000    100 "" 3 7) >1-onemax/result/result-ts-om-100.txt 2>&1

(time ./2-deception/search tsdp  100 1000      4 "" 3 7) >2-deception/result/result-tsdp-deception-4.txt 2>&1
(time ./2-deception/search tsdp  100 1000     10 "" 3 7) >2-deception/result/result-tsdp-deception-10.txt 2>&1

set +x
