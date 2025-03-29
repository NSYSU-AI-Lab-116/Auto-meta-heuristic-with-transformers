#!/usr/bin/env bash

set -x

source search.conf

(time ./1-onemax/search se 100 10000 10  "" 4 4 2 3 0) >1-onemax/result/result-se-10-44.txt 2>&1
(time ./1-onemax/search se 100 10000 20  "" 4 4 2 3 0) >1-onemax/result/result-se-20-44.txt 2>&1
(time ./1-onemax/search se 100 10000 40  "" 4 4 2 3 0) >1-onemax/result/result-se-40-44.txt 2>&1
(time ./1-onemax/search se 100 10000 60  "" 4 4 2 3 0) >1-onemax/result/result-se-60-44.txt 2>&1
(time ./1-onemax/search se 100 10000 80  "" 4 4 2 3 0) >1-onemax/result/result-se-80-44.txt 2>&1
(time ./1-onemax/search se 100 10000 100 "" 4 4 2 3 0) >1-onemax/result/result-se-100-44.txt 2>&1

(time ./1-onemax/search se 100 10000 10  "" 1 2 1 1 0) >1-onemax/result/result-se-10-21.txt 2>&1
(time ./1-onemax/search se 100 10000 20  "" 1 2 1 1 0) >1-onemax/result/result-se-20-21.txt 2>&1
(time ./1-onemax/search se 100 10000 40  "" 1 2 1 1 0) >1-onemax/result/result-se-40-21.txt 2>&1
(time ./1-onemax/search se 100 10000 60  "" 1 2 1 1 0) >1-onemax/result/result-se-60-21.txt 2>&1
(time ./1-onemax/search se 100 10000 80  "" 1 2 1 1 0) >1-onemax/result/result-se-80-21.txt 2>&1
(time ./1-onemax/search se 100 10000 100 "" 1 2 1 1 0) >1-onemax/result/result-se-100-21.txt 2>&1

(time ./1-onemax/search se 100 10000 10  "" 1 1 1 1 0) >1-onemax/result/result-se-10-11.txt 2>&1
(time ./1-onemax/search se 100 10000 20  "" 1 1 1 1 0) >1-onemax/result/result-se-20-11.txt 2>&1
(time ./1-onemax/search se 100 10000 40  "" 1 1 1 1 0) >1-onemax/result/result-se-40-11.txt 2>&1
(time ./1-onemax/search se 100 10000 60  "" 1 1 1 1 0) >1-onemax/result/result-se-60-11.txt 2>&1
(time ./1-onemax/search se 100 10000 80  "" 1 1 1 1 0) >1-onemax/result/result-se-80-11.txt 2>&1
(time ./1-onemax/search se 100 10000 100 "" 1 1 1 1 0) >1-onemax/result/result-se-100-11.txt 2>&1

(time ./1-onemax/search se 1 10000 10  "" 1 2 1 1 1)   >1-onemax/result/result-se-10-21-scater.txt 2>&1
(time ./1-onemax/search se 1 10000 10  "" 4 4 2 3 1)   >1-onemax/result/result-se-10-44-scater.txt 2>&1

(time ./1-onemax/search se 100 10000 100 "" 1 1 1 1 1) >1-onemax/result/result-se-100-21-scater.txt 2>&1
(time ./1-onemax/search se 100 10000 100 "" 4 4 2 3 1) >1-onemax/result/result-se-100-44-scater.txt 2>&1

set +x

