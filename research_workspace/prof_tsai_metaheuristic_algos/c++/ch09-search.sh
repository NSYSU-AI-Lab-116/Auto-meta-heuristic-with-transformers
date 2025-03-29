#!/usr/bin/env bash

set -x

source search.conf

(time ./4-function/search pso 100 1000 2 "" "mvfAckley" 10 0.5 1.5 1.5 -32.0 32.0) >4-function/result/result-pso-mvfackley-2.txt 2>&1
(time ./4-function/search pso 100 1000 2 "" "mvfAckley" 10 0.5 1.0 1.5 -32.0 32.0) >4-function/result/result-pso-mvfackley-2-051015.txt 2>&1

set +x
