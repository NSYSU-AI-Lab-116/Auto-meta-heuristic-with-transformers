#!/usr/bin/env python
import math
import matplotlib.pyplot as plt
import numpy as np
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
    x = np.linspace(-1000, 1000, 100000)
    y = np.linspace(-1000, 1000, 100000)
    X,Y = np.meshgrid(x,y)
    Z = np.vectorize(mvfAckley)(2, [X,Y])
    ax = plt.axes(projection='3d')
    ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
    plt.title("Ackley Function")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    plt.show()
    
    pass
