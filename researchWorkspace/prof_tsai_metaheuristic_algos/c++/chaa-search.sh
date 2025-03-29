#!/usr/bin/env bash

set -x

source search.conf

(time ./1-onemax/search hc_r 100 1000 30 "") >1-onemax/result/result-hc-om-random-30.txt 2>&1
(time ./1-onemax/search hc_r 100 1000 50 "") >1-onemax/result/result-hc-om-random-50.txt 2>&1
(time ./1-onemax/search hc_r 100 1000 70 "") >1-onemax/result/result-hc-om-random-70.txt 2>&1
(time ./1-onemax/search hc_r 100 1000 90 "") >1-onemax/result/result-hc-om-random-90.txt 2>&1

(time ./1-onemax/search sa   100 1000 30 "" 0.00001 1.0) >1-onemax/result/result-sa-om-30.txt 2>&1 
(time ./1-onemax/search sa   100 1000 50 "" 0.00001 1.0) >1-onemax/result/result-sa-om-50.txt 2>&1 
(time ./1-onemax/search sa   100 1000 70 "" 0.00001 1.0) >1-onemax/result/result-sa-om-70.txt 2>&1 
(time ./1-onemax/search sa   100 1000 90 "" 0.00001 1.0) >1-onemax/result/result-sa-om-90.txt 2>&1 

(time ./1-onemax/search ga   100 100000 100 "" 10 0.6 0.02 3) >1-onemax/result/result-ga-100-02.txt 2>&1
(time ./1-onemax/search ga   100 100000 100 "" 10 0.6 0.03 3) >1-onemax/result/result-ga-100-03.txt 2>&1
(time ./1-onemax/search ga   100 100000 100 "" 10 0.6 0.04 3) >1-onemax/result/result-ga-100-04.txt 2>&1
(time ./1-onemax/search ga   100 100000 100 "" 10 0.6 0.05 3) >1-onemax/result/result-ga-100-05.txt 2>&1
(time ./1-onemax/search ga   100 100000 100 "" 10 0.6 0.06 3) >1-onemax/result/result-ga-100-06.txt 2>&1
(time ./1-onemax/search ga   100 100000 100 "" 10 0.6 0.07 3) >1-onemax/result/result-ga-100-07.txt 2>&1
(time ./1-onemax/search ga   100 100000 100 "" 10 0.6 0.08 3) >1-onemax/result/result-ga-100-08.txt 2>&1
(time ./1-onemax/search ga   100 100000 100 "" 10 0.6 0.09 3) >1-onemax/result/result-ga-100-09.txt 2>&1
(time ./1-onemax/search ga   100 100000 100 "" 10 0.6 0.10 3) >1-onemax/result/result-ga-100-10.txt 2>&1

(time ./1-onemax/search gax2 100 100000 100 "" 10 0.6 0.01 3) >1-onemax/result/result-ga-100-twopoint.txt 2>&1
(time ./1-onemax/search gaxu 100 100000 100 "" 10 0.6 0.01 3) >1-onemax/result/result-ga-100-uniform.txt 2>&1

set +x
