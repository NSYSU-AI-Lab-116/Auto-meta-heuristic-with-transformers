#!/usr/bin/env bash

set -x

source search.conf

(time ./6-clustering/search ga    100 1000 150 4 3   "" "6-clustering/iris.data"    20 0.6 0.1 3 1)          >6-clustering/result/result-ga-iris-analysis.txt 2>&1 
(time ./6-clustering/search prega 100 1000 150 4 3   "" "6-clustering/iris.data"    20 0.6 0.1 3 80  0.1 1)  >6-clustering/result/result-prega-iris-analysis.txt 2>&1 

(time ./6-clustering/search ga    100 1000 4177 8 29 "" "6-clustering/abalone.data" 20 0.6 0.1 3 1)          >6-clustering/result/result-ga-abalone-analysis.txt 2>&1 
(time ./6-clustering/search prega 100 1000 4177 8 29 "" "6-clustering/abalone.data" 20 0.6 0.1 3 80  0.1 1)  >6-clustering/result/result-prega-abalone-analysis.txt 2>&1 

(time ./6-clustering/search ga    100 400 150 4 3    "" "6-clustering/iris.data"    20 0.6 0.1 3 0)          >6-clustering/result/result-ga-iris.txt 2>&1 
(time ./6-clustering/search prega 100 400 150 4 3    "" "6-clustering/iris.data"    20 0.6 0.1 3 80  0.1 0)  >6-clustering/result/result-prega-iris.txt 2>&1 

(time ./6-clustering/search ga    100 1000 4177 8 29 "" "6-clustering/abalone.data" 20 0.6 0.1 3 0)          >6-clustering/result/result-ga-abalone.txt 2>&1 

(time ./6-clustering/search prega 100 1000 4177 8 29 "" "6-clustering/abalone.data" 20 0.6 0.1 3 40  0.1 0)  >6-clustering/result/result-prega-abalone-s40.txt 2>&1 
(time ./6-clustering/search prega 100 1000 4177 8 29 "" "6-clustering/abalone.data" 20 0.6 0.1 3 60  0.1 0)  >6-clustering/result/result-prega-abalone-s60.txt 2>&1 
(time ./6-clustering/search prega 100 1000 4177 8 29 "" "6-clustering/abalone.data" 20 0.6 0.1 3 80  0.1 0)  >6-clustering/result/result-prega-abalone-s80.txt 2>&1 
(time ./6-clustering/search prega 100 1000 4177 8 29 "" "6-clustering/abalone.data" 20 0.6 0.1 3 100 0.1 0)  >6-clustering/result/result-prega-abalone-s100.txt 2>&1 
(time ./6-clustering/search prega 100 1000 4177 8 29 "" "6-clustering/abalone.data" 20 0.6 0.1 3 120 0.1 0)  >6-clustering/result/result-prega-abalone-s120.txt 2>&1 
(time ./6-clustering/search prega 100 1000 4177 8 29 "" "6-clustering/abalone.data" 20 0.6 0.1 3 160 0.1 0)  >6-clustering/result/result-prega-abalone-s160.txt 2>&1 
(time ./6-clustering/search prega 100 1000 4177 8 29 "" "6-clustering/abalone.data" 20 0.6 0.1 3 180 0.1 0)  >6-clustering/result/result-prega-abalone-s180.txt 2>&1 
(time ./6-clustering/search prega 100 1000 4177 8 29 "" "6-clustering/abalone.data" 20 0.6 0.1 3 200 0.1 0)  >6-clustering/result/result-prega-abalone-s200.txt 2>&1 


(time ./6-clustering/search prega 100 1000 4177 8 29 "" "6-clustering/abalone.data" 20 0.6 0.1 3 80 0.01 0)  >6-clustering/result/result-prega-abalone-s80-r001.txt 2>&1 
(time ./6-clustering/search prega 100 1000 4177 8 29 "" "6-clustering/abalone.data" 20 0.6 0.1 3 80 0.02 0)  >6-clustering/result/result-prega-abalone-s80-r002.txt 2>&1 
(time ./6-clustering/search prega 100 1000 4177 8 29 "" "6-clustering/abalone.data" 20 0.6 0.1 3 80 0.06 0)  >6-clustering/result/result-prega-abalone-s80-r006.txt 2>&1 
(time ./6-clustering/search prega 100 1000 4177 8 29 "" "6-clustering/abalone.data" 20 0.6 0.1 3 80 0.08 0)  >6-clustering/result/result-prega-abalone-s80-r008.txt 2>&1 
(time ./6-clustering/search prega 100 1000 4177 8 29 "" "6-clustering/abalone.data" 20 0.6 0.1 3 80 0.2  0)  >6-clustering/result/result-prega-abalone-s80-r02.txt 2>&1 
(time ./6-clustering/search prega 100 1000 4177 8 29 "" "6-clustering/abalone.data" 20 0.6 0.1 3 80 0.4  0)  >6-clustering/result/result-prega-abalone-s80-r04.txt 2>&1 
(time ./6-clustering/search prega 100 1000 4177 8 29 "" "6-clustering/abalone.data" 20 0.6 0.1 3 80 0.6  0)  >6-clustering/result/result-prega-abalone-s80-r06.txt 2>&1 

set +x
