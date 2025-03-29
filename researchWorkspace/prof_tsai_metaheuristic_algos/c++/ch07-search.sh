#!/usr/bin/env bash

set -x

source search.conf

(time ./1-onemax/search ga       100   1000  10 "" 10 0.6 0.01 3)  >1-onemax/result/result-ga-10.txt 2>&1
(time ./1-onemax/search ga       100   1000  20 "" 10 0.6 0.01 3)  >1-onemax/result/result-ga-20.txt 2>&1
(time ./1-onemax/search ga       100   1000  40 "" 10 0.6 0.01 3)  >1-onemax/result/result-ga-40.txt 2>&1
(time ./1-onemax/search ga       100   1000  60 "" 10 0.6 0.01 3)  >1-onemax/result/result-ga-60.txt 2>&1
(time ./1-onemax/search ga       100   1000  80 "" 10 0.6 0.01 3)  >1-onemax/result/result-ga-80.txt 2>&1
(time ./1-onemax/search ga       100  50000 100 "" 10 0.6 0.01 3)  >1-onemax/result/result-ga-100.txt 2>&1
(time ./1-onemax/search gaxu     100  50000 100 "" 10 0.6 0.01 3)  >1-onemax/result/result-gaxu-100.txt 2>&1

(time ./1-onemax/search gar      100   1000  10 "" 10 0.6 0.01 0)  >1-onemax/result/result-gar-10.txt 2>&1 
(time ./1-onemax/search gar      100   1000  20 "" 10 0.6 0.01 0)  >1-onemax/result/result-gar-20.txt 2>&1 
(time ./1-onemax/search gar      100   1000  40 "" 10 0.6 0.01 0)  >1-onemax/result/result-gar-40.txt 2>&1 
(time ./1-onemax/search gar      100   1000  60 "" 10 0.6 0.01 0)  >1-onemax/result/result-gar-60.txt 2>&1 
(time ./1-onemax/search gar      100   1000  80 "" 10 0.6 0.01 0)  >1-onemax/result/result-gar-80.txt 2>&1 
(time ./1-onemax/search gar      100  50000 100 "" 10 0.6 0.01 0)  >1-onemax/result/result-gar-100.txt 2>&1 

(time ./2-deception/search gadp  100   1000   4 "" 10 0.6 0.01 3)  >2-deception/result/result-gadp-4.txt 2>&1
(time ./2-deception/search gadp  100   1000  10 "" 10 0.6 0.01 3)  >2-deception/result/result-gadp-10.txt 2>&1

(time ./2-deception/search gardp 100   1000   4 "" 10 0.6 0.01 0)  >2-deception/result/result-gardp-4.txt 2>&1
(time ./2-deception/search gardp 100   1000  10 "" 10 0.6 0.01 0)  >2-deception/result/result-gardp-10.txt 2>&1

(time ./1-onemax/search gaxu     100   5000 100 "" 10 0.6 0.01 4)  >1-onemax/result/result-gaxu-100-4.txt 2>&1
(time ./1-onemax/search gaxu     100   5000 100 "" 10 0.6 0.01 5)  >1-onemax/result/result-gaxu-100-5.txt 2>&1
(time ./1-onemax/search gaxu     100   5000 100 "" 10 0.6 0.01 6)  >1-onemax/result/result-gaxu-100-6.txt 2>&1
(time ./1-onemax/search gaxu     100   5000 100 "" 10 0.6 0.01 7)  >1-onemax/result/result-gaxu-100-7.txt 2>&1
(time ./1-onemax/search gaxu     100   5000 100 "" 10 0.6 0.01 8)  >1-onemax/result/result-gaxu-100-8.txt 2>&1
(time ./1-onemax/search gaxu     100   5000 100 "" 10 0.6 0.01 9)  >1-onemax/result/result-gaxu-100-9.txt 2>&1
(time ./1-onemax/search gaxu     100   5000 100 "" 10 0.6 0.01 10) >1-onemax/result/result-gaxu-100-10.txt 2>&1
(time ./2-deception/search gadp  100   1000  10 "" 10 0.6 0.01 4)  >2-deception/result/result-gadp-10-4.txt 2>&1
(time ./2-deception/search gadp  100   1000  10 "" 10 0.6 0.01 5)  >2-deception/result/result-gadp-10-5.txt 2>&1
(time ./2-deception/search gadp  100   1000  10 "" 10 0.6 0.01 6)  >2-deception/result/result-gadp-10-6.txt 2>&1
(time ./2-deception/search gadp  100   1000  10 "" 10 0.6 0.01 7)  >2-deception/result/result-gadp-10-7.txt 2>&1
(time ./2-deception/search gadp  100   1000  10 "" 10 0.6 0.01 8)  >2-deception/result/result-gadp-10-8.txt 2>&1
(time ./2-deception/search gadp  100   1000  10 "" 10 0.6 0.01 9)  >2-deception/result/result-gadp-10-9.txt 2>&1
(time ./2-deception/search gadp  100   1000  10 "" 10 0.6 0.01 10) >2-deception/result/result-gadp-10-10.txt 2>&1

set +x
