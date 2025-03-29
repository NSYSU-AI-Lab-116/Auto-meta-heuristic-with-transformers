#!/usr/bin/env python
import math

sqrt = math.sqrt
sin = math.sin
cos = math.cos
exp = math.exp
pi = math.pi

def mvfAckley(n, x):
    s1 = s2 = 0.0
    for i in range(n):
        s1 += x[i] * x[i]
        s2 += cos(2.0 * pi * x[i])
    return -20.0 * exp(-0.2 * sqrt(s1/n)) + 20.0 - exp(s2/n) + exp(1.0)

function_table = {
    "mvfAckley": mvfAckley
}

if __name__ == "__main__":
    pass
