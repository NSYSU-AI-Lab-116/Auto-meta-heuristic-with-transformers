#!/usr/bin/env bash

set -x

source search.conf

(time ./3-tsp/search hga 100 120000 51 "" "3-tsp/eil51.tsp" 120 0.4 0.1 3  10 0.1 1.0 0.00001) >3-tsp/result/result-gasa-100-01-10.txt 2>&1 
(time ./3-tsp/search hga 100 120000 51 "" "3-tsp/eil51.tsp" 120 0.4 0.1 3  20 0.1 1.0 0.00001) >3-tsp/result/result-gasa-100-01-20.txt 2>&1 
(time ./3-tsp/search hga 100 120000 51 "" "3-tsp/eil51.tsp" 120 0.4 0.1 3  40 0.1 1.0 0.00001) >3-tsp/result/result-gasa-100-01-40.txt 2>&1 
(time ./3-tsp/search hga 100 120000 51 "" "3-tsp/eil51.tsp" 120 0.4 0.1 3  60 0.1 1.0 0.00001) >3-tsp/result/result-gasa-100-01-60.txt 2>&1 
(time ./3-tsp/search hga 100 120000 51 "" "3-tsp/eil51.tsp" 120 0.4 0.1 3  80 0.1 1.0 0.00001) >3-tsp/result/result-gasa-100-01-80.txt 2>&1 
(time ./3-tsp/search hga 100 120000 51 "" "3-tsp/eil51.tsp" 120 0.4 0.1 3 100 0.1 1.0 0.00001) >3-tsp/result/result-gasa-100-01-100.txt 2>&1 

(time ./3-tsp/search hga 100 120000 51 "" "3-tsp/eil51.tsp" 120 0.4 0.1 3  10 0.2 1.0 0.00001) >3-tsp/result/result-gasa-100-02-10.txt 2>&1 
(time ./3-tsp/search hga 100 120000 51 "" "3-tsp/eil51.tsp" 120 0.4 0.1 3  10 0.4 1.0 0.00001) >3-tsp/result/result-gasa-100-04-10.txt 2>&1 
(time ./3-tsp/search hga 100 120000 51 "" "3-tsp/eil51.tsp" 120 0.4 0.1 3  10 0.6 1.0 0.00001) >3-tsp/result/result-gasa-100-06-10.txt 2>&1 
(time ./3-tsp/search hga 100 120000 51 "" "3-tsp/eil51.tsp" 120 0.4 0.1 3  10 0.8 1.0 0.00001) >3-tsp/result/result-gasa-100-08-10.txt 2>&1 

(time ./3-tsp/search hga 100 120000 51 "" "3-tsp/eil51.tsp" 120 0.4 0.1 3 100 0.2 1.0 0.00001) >3-tsp/result/result-gasa-100-02-100.txt 2>&1 
(time ./3-tsp/search hga 100 120000 51 "" "3-tsp/eil51.tsp" 120 0.4 0.1 3 100 0.4 1.0 0.00001) >3-tsp/result/result-gasa-100-04-100.txt 2>&1 
(time ./3-tsp/search hga 100 120000 51 "" "3-tsp/eil51.tsp" 120 0.4 0.1 3 100 0.6 1.0 0.00001) >3-tsp/result/result-gasa-100-06-100.txt 2>&1 
(time ./3-tsp/search hga 100 120000 51 "" "3-tsp/eil51.tsp" 120 0.4 0.1 3 100 0.8 1.0 0.00001) >3-tsp/result/result-gasa-100-08-100.txt 2>&1 

set +x
