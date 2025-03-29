#!/usr/bin/env bash

set -x

source search.conf

(time ./3-tsp/search gals 100 120000 51   "" "3-tsp/eil51.tsp"  100 0.4 0.1 3 100 0)  >3-tsp/result/result-gals-ch17-2opt-100-0.txt 2>&1
(time ./3-tsp/search gals 100 120000 51   "" "3-tsp/eil51.tsp"  100 0.4 0.1 3 200 0)  >3-tsp/result/result-gals-ch17-2opt-200-0.txt 2>&1
(time ./3-tsp/search gals 100 120000 51   "" "3-tsp/eil51.tsp"  100 0.4 0.1 3 400 0)  >3-tsp/result/result-gals-ch17-2opt-400-0.txt 2>&1
(time ./3-tsp/search gals 100 120000 51   "" "3-tsp/eil51.tsp"  100 0.4 0.1 3 600 0)  >3-tsp/result/result-gals-ch17-2opt-600-0.txt 2>&1
(time ./3-tsp/search gals 100 120000 51   "" "3-tsp/eil51.tsp"  100 0.4 0.1 3 800 0)  >3-tsp/result/result-gals-ch17-2opt-800-0.txt 2>&1
(time ./3-tsp/search gals 100 120000 51   "" "3-tsp/eil51.tsp"  100 0.4 0.1 3 1000 0) >3-tsp/result/result-gals-ch17-2opt-1000-0.txt 2>&1

(time ./3-tsp/search gals 100 120000 51   "" "3-tsp/eil51.tsp"  100 0.4 0.1 3 100 1)  >3-tsp/result/result-gals-ch17-2opt-100-1.txt 2>&1
(time ./3-tsp/search gals 100 120000 51   "" "3-tsp/eil51.tsp"  100 0.4 0.1 3 200 1)  >3-tsp/result/result-gals-ch17-2opt-200-1.txt 2>&1
(time ./3-tsp/search gals 100 120000 51   "" "3-tsp/eil51.tsp"  100 0.4 0.1 3 400 1)  >3-tsp/result/result-gals-ch17-2opt-400-1.txt 2>&1
(time ./3-tsp/search gals 100 120000 51   "" "3-tsp/eil51.tsp"  100 0.4 0.1 3 600 1)  >3-tsp/result/result-gals-ch17-2opt-600-1.txt 2>&1
(time ./3-tsp/search gals 100 120000 51   "" "3-tsp/eil51.tsp"  100 0.4 0.1 3 800 1)  >3-tsp/result/result-gals-ch17-2opt-800-1.txt 2>&1
(time ./3-tsp/search gals 100 120000 51   "" "3-tsp/eil51.tsp"  100 0.4 0.1 3 1000 1) >3-tsp/result/result-gals-ch17-2opt-1000-1.txt 2>&1

(time ./3-tsp/search gaox 100 120000  51  "" "3-tsp/eil51.tsp"  120 0.2 0.1 3)        >3-tsp/result/result-ox-0201-1200000.txt 2>&1
(time ./3-tsp/search gals 100 1200000 51  "" "3-tsp/eil51.tsp"  100 0.4 0.1 3 1000 0) >3-tsp/result/result-gals-ch17-2opt-100-0-1200000.txt 2>&1
(time ./3-tsp/search gals 100 1200000 51  "" "3-tsp/eil51.tsp"  100 0.4 0.1 3 1000 1) >3-tsp/result/result-gals-ch17-2opt-100-1-1200000.txt 2>&1

set +x
