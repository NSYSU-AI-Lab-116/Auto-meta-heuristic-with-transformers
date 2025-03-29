#!/usr/bin/env bash

set -x

source search.conf

(time ./4-function/search de    100 1000 2 "" "mvfAckley" 10 0.7 0.5 -32.0 32.0) >4-function/result/result-de-mvfackley-2.txt 2>&1
(time ./4-function/search deb1  100 1000 2 "" "mvfAckley" 10 0.7 0.5 -32.0 32.0) >4-function/result/result-deb1-mvfackley-2.txt 2>&1
(time ./4-function/search decb1 100 1000 2 "" "mvfAckley" 10 0.7 0.5 -32.0 32.0) >4-function/result/result-decb1-mvfackley-2.txt 2>&1
(time ./4-function/search deb2  100 1000 2 "" "mvfAckley" 10 0.7 0.5 -32.0 32.0) >4-function/result/result-deb2-mvfackley-2.txt 2>&1
(time ./4-function/search der2  100 1000 2 "" "mvfAckley" 10 0.7 0.5 -32.0 32.0) >4-function/result/result-der2-mvfackley-2.txt 2>&1

set +x
