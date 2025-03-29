#!/usr/bin/env bash

set -x

source search.conf

(time ./3-tsp/search ga    100 120000  51 "" "3-tsp/eil51.tsp" 120 0.2 0.1 3) >3-tsp/result/result-mopc-0201.txt 2>&1
(time ./3-tsp/search gapmx 100 120000  51 "" "3-tsp/eil51.tsp" 120 0.2 0.1 3) >3-tsp/result/result-pmx-0201.txt 2>&1
(time ./3-tsp/search gacx  100 120000  51 "" "3-tsp/eil51.tsp" 120 0.2 0.1 3) >3-tsp/result/result-cx-0201.txt 2>&1
(time ./3-tsp/search gaox  100 120000  51 "" "3-tsp/eil51.tsp" 120 0.2 0.1 3) >3-tsp/result/result-ox-0201.txt 2>&1

(time ./3-tsp/search ga    100 120000  51 "" "3-tsp/eil51.tsp" 120 0.4 0.1 3) >3-tsp/result/result-mopc-0401.txt 2>&1
(time ./3-tsp/search gapmx 100 120000  51 "" "3-tsp/eil51.tsp" 120 0.4 0.1 3) >3-tsp/result/result-pmx-0401.txt 2>&1
(time ./3-tsp/search gacx  100 120000  51 "" "3-tsp/eil51.tsp" 120 0.4 0.1 3) >3-tsp/result/result-cx-0401.txt 2>&1
(time ./3-tsp/search gaox  100 120000  51 "" "3-tsp/eil51.tsp" 120 0.4 0.1 3) >3-tsp/result/result-ox-0401.txt 2>&1

(time ./3-tsp/search ga    100 120000  51 "" "3-tsp/eil51.tsp" 120 0.6 0.1 3) >3-tsp/result/result-mopc-0601.txt 2>&1
(time ./3-tsp/search gapmx 100 120000  51 "" "3-tsp/eil51.tsp" 120 0.6 0.1 3) >3-tsp/result/result-pmx-0601.txt 2>&1
(time ./3-tsp/search gacx  100 120000  51 "" "3-tsp/eil51.tsp" 120 0.6 0.1 3) >3-tsp/result/result-cx-0601.txt 2>&1
(time ./3-tsp/search gaox  100 120000  51 "" "3-tsp/eil51.tsp" 120 0.6 0.1 3) >3-tsp/result/result-ox-0601.txt 2>&1

(time ./3-tsp/search ga    100 120000  51 "" "3-tsp/eil51.tsp" 120 0.8 0.1 3) >3-tsp/result/result-mopc-0801.txt 2>&1
(time ./3-tsp/search gapmx 100 120000  51 "" "3-tsp/eil51.tsp" 120 0.8 0.1 3) >3-tsp/result/result-pmx-0801.txt 2>&1
(time ./3-tsp/search gacx  100 120000  51 "" "3-tsp/eil51.tsp" 120 0.8 0.1 3) >3-tsp/result/result-cx-0801.txt 2>&1
(time ./3-tsp/search gaox  100 120000  51 "" "3-tsp/eil51.tsp" 120 0.8 0.1 3) >3-tsp/result/result-ox-0801.txt 2>&1

set +x
