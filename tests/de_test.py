import os, sys
import time
sys.path.insert(0, os.path.abspath("src/cpp/build"))
from DE_cpp import run as de_run
import numpy as np

f = lambda x: np.sum(x**2)
pop = np.random.rand(20,  10)
start = time.perf_counter()
pop2, curve = de_run(pop, f, 0.5, 0.9, 100)
end = time.perf_counter()
print(f"Execution time: {end - start:.4f} seconds")
print(pop2.shape, curve.shape)
print(curve)