#!/usr/bin/env bash

set -x

source search.conf

cp -a 3-tsp/result/result-ox-0401.txt 3-tsp/result/result-ox-0401-120.txt

(time ./3-tsp/search gaox 100 120000   51 "" "3-tsp/eil51.tsp" 240 0.4 0.1 3)    >3-tsp/result/result-ox-0401-240.txt 2>&1

(time ./3-tsp/search gaox 100 120000   51 "" "3-tsp/eil51.tsp" 240 0.4 0.1 3)    >3-tsp/result/result-ox-0401-240.txt 2>&1
(time ./3-tsp/search gaox 100 120000   51 "" "3-tsp/eil51.tsp" 480 0.4 0.1 3)    >3-tsp/result/result-ox-0401-480.txt 2>&1
(time ./3-tsp/search gaox 100 120000   51 "" "3-tsp/eil51.tsp" 960 0.4 0.1 3)    >3-tsp/result/result-ox-0401-960.txt 2>&1

(time ./3-tsp/search pga  100 120000   51 "" "3-tsp/eil51.tsp" 120 0.4 0.1 3 4)  >3-tsp/result/result-eil51-pga120-4.txt 2>&1
(time ./3-tsp/search pga  100 120000   51 "" "3-tsp/eil51.tsp" 240 0.4 0.1 3 4)  >3-tsp/result/result-eil51-pga240-4.txt 2>&1
(time ./3-tsp/search pga  100 120000   51 "" "3-tsp/eil51.tsp" 480 0.4 0.1 3 4)  >3-tsp/result/result-eil51-pga480-4.txt 2>&1
(time ./3-tsp/search pga  100 120000   51 "" "3-tsp/eil51.tsp" 960 0.4 0.1 3 4)  >3-tsp/result/result-eil51-pga960-4.txt 2>&1

(time ./3-tsp/search gaox 100 120000 1002 "" "3-tsp/pr1002.tsp" 120 0.4 0.1 3)   >3-tsp/result/result-ox-pr1002-0401-120.txt 2>&1
(time ./3-tsp/search gaox 100 120000 1002 "" "3-tsp/pr1002.tsp" 240 0.4 0.1 3)   >3-tsp/result/result-ox-pr1002-0401-240.txt 2>&1
(time ./3-tsp/search gaox 100 120000 1002 "" "3-tsp/pr1002.tsp" 480 0.4 0.1 3)   >3-tsp/result/result-ox-pr1002-0401-480.txt 2>&1
(time ./3-tsp/search gaox 100 120000 1002 "" "3-tsp/pr1002.tsp" 960 0.4 0.1 3)   >3-tsp/result/result-ox-pr1002-0401-960.txt 2>&1

(time ./3-tsp/search pga  100 120000 1002 "" "3-tsp/pr1002.tsp" 120 0.4 0.1 3 2) >3-tsp/result/result-pr1002-pga120-2.txt 2>&1
(time ./3-tsp/search pga  100 120000 1002 "" "3-tsp/pr1002.tsp" 120 0.4 0.1 3 4) >3-tsp/result/result-pr1002-pga120-4.txt 2>&1
(time ./3-tsp/search pga  100 120000 1002 "" "3-tsp/pr1002.tsp" 120 0.4 0.1 3 6) >3-tsp/result/result-pr1002-pga120-6.txt 2>&1
(time ./3-tsp/search pga  100 120000 1002 "" "3-tsp/pr1002.tsp" 120 0.4 0.1 3 8) >3-tsp/result/result-pr1002-pga120-8.txt 2>&1

(time ./3-tsp/search pga  100 120000 1002 "" "3-tsp/pr1002.tsp" 240 0.4 0.1 3 2) >3-tsp/result/result-pr1002-pga240-2.txt 2>&1
(time ./3-tsp/search pga  100 120000 1002 "" "3-tsp/pr1002.tsp" 240 0.4 0.1 3 4) >3-tsp/result/result-pr1002-pga240-4.txt 2>&1
(time ./3-tsp/search pga  100 120000 1002 "" "3-tsp/pr1002.tsp" 240 0.4 0.1 3 6) >3-tsp/result/result-pr1002-pga240-6.txt 2>&1
(time ./3-tsp/search pga  100 120000 1002 "" "3-tsp/pr1002.tsp" 240 0.4 0.1 3 8) >3-tsp/result/result-pr1002-pga240-8.txt 2>&1

(time ./3-tsp/search pga  100 120000 1002 "" "3-tsp/pr1002.tsp" 480 0.4 0.1 3 2) >3-tsp/result/result-pr1002-pga480-2.txt 2>&1
(time ./3-tsp/search pga  100 120000 1002 "" "3-tsp/pr1002.tsp" 480 0.4 0.1 3 4) >3-tsp/result/result-pr1002-pga480-4.txt 2>&1
(time ./3-tsp/search pga  100 120000 1002 "" "3-tsp/pr1002.tsp" 480 0.4 0.1 3 6) >3-tsp/result/result-pr1002-pga480-6.txt 2>&1
(time ./3-tsp/search pga  100 120000 1002 "" "3-tsp/pr1002.tsp" 480 0.4 0.1 3 8) >3-tsp/result/result-pr1002-pga480-8.txt 2>&1

(time ./3-tsp/search pga  100 120000 1002 "" "3-tsp/pr1002.tsp" 960 0.4 0.1 3 2) >3-tsp/result/result-pr1002-pga960-2.txt 2>&1
(time ./3-tsp/search pga  100 120000 1002 "" "3-tsp/pr1002.tsp" 960 0.4 0.1 3 4) >3-tsp/result/result-pr1002-pga960-4.txt 2>&1
(time ./3-tsp/search pga  100 120000 1002 "" "3-tsp/pr1002.tsp" 960 0.4 0.1 3 6) >3-tsp/result/result-pr1002-pga960-6.txt 2>&1
(time ./3-tsp/search pga  100 120000 1002 "" "3-tsp/pr1002.tsp" 960 0.4 0.1 3 8) >3-tsp/result/result-pr1002-pga960-8.txt 2>&1

set +x
