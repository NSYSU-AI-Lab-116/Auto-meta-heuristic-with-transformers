#!/usr/bin/env bash

set -x

source search.conf

(time ./1-onemax/search sa_refinit 100 1000 100 "" 0.00001 1.0 10  2) >1-onemax/result/result-sa_refinit-om-100-2.txt 2>&1 
(time ./1-onemax/search sa_refinit 100 1000 100 "" 0.00001 1.0 10  4) >1-onemax/result/result-sa_refinit-om-100-4.txt 2>&1 
(time ./1-onemax/search sa_refinit 100 1000 100 "" 0.00001 1.0 10  5) >1-onemax/result/result-sa_refinit-om-100-5.txt 2>&1 
(time ./1-onemax/search sa_refinit 100 1000 100 "" 0.00001 1.0 10 10) >1-onemax/result/result-sa_refinit-om-100-10.txt 2>&1 
(time ./1-onemax/search sa_refinit 100 1000 100 "" 0.00001 1.0 10 20) >1-onemax/result/result-sa_refinit-om-100-20.txt 2>&1 

set +x
