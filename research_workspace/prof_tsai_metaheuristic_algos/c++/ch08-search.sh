#!/usr/bin/env bash

set -x

source search.conf

(time ./3-tsp/search aco 100 25000 51 "" "3-tsp/eil51.tsp" 20 0.1 2.0 0.1 0.9) >3-tsp/result/result-aco-tsp-eil51.txt 2>&1

set +x
