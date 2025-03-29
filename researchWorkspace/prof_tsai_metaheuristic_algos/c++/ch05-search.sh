#!/usr/bin/env bash

set -x

source search.conf

(time ./1-onemax/search hc_r    100 1000     20 "")             >1-onemax/result/result-hc-om-random-20.txt 2>&1
(time ./1-onemax/search hc_r    100 1000     40 "")             >1-onemax/result/result-hc-om-random-40.txt 2>&1
(time ./1-onemax/search hc_r    100 1000     60 "")             >1-onemax/result/result-hc-om-random-60.txt 2>&1
(time ./1-onemax/search hc_r    100 1000     80 "")             >1-onemax/result/result-hc-om-random-80.txt 2>&1
(time ./1-onemax/search hc_r    100 1000    100 "")             >1-onemax/result/result-hc-om-random-100.txt 2>&1

(time ./1-onemax/search sa      100 1000     10 "" 0.00001 1.0) >1-onemax/result/result-sa-om-10.txt 2>&1 
(time ./1-onemax/search sa      100 1000     20 "" 0.00001 1.0) >1-onemax/result/result-sa-om-20.txt 2>&1 
(time ./1-onemax/search sa      100 1000     40 "" 0.00001 1.0) >1-onemax/result/result-sa-om-40.txt 2>&1 
(time ./1-onemax/search sa      100 1000     60 "" 0.00001 1.0) >1-onemax/result/result-sa-om-60.txt 2>&1 
(time ./1-onemax/search sa      100 1000     80 "" 0.00001 1.0) >1-onemax/result/result-sa-om-80.txt 2>&1 
(time ./1-onemax/search sa      100 1000    100 "" 0.00001 1.0) >1-onemax/result/result-sa-om-100.txt 2>&1 
(time ./2-deception/search sadp 100 1000      4 "" 0.00001 1.0) >2-deception/result/result-sadp-deception-4.txt 2>&1
(time ./2-deception/search sadp 100 1000     10 "" 0.00001 1.0) >2-deception/result/result-sadp-deception-10.txt 2>&1

set +x
