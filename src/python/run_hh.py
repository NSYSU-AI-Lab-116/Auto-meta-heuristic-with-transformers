import os, numpy as np
from pathlib import Path
from src.python.Config import Configs
from src.python.Optimizer import HyperParameters
from src.python.hyperheuristic import HyperHeuristicTemplate

FUNC_TYPE, YEAR, NAME, DIM = "CEC", "2021", "F9", 10
ITER, TRIALS = 1500, 6    

root = Path("research_workspace/auto-metaheuristic/exp_result")
folder = root / "hh_result"
data_dir = folder / "data"
data_dir.mkdir(parents=True, exist_ok=True)

obj_func = Configs.DataSet.get_function(FUNC_TYPE, YEAR, NAME, DIM)


all_curves, first80 = [], []
for ep in range(TRIALS):
    _, curve = HyperHeuristicTemplate(
        obj_function=obj_func, hyper_iteration=ITER, color=""
    ).start()
    all_curves.append(curve)
    tgt = curve[-1] + 0.15 * (curve[0] - curve[-1])
    first80.append(next(i for i,v in enumerate(curve) if v<=tgt))

all_curves = np.array(all_curves)
np.save(data_dir/"all_curves.npy", all_curves)
np.save(data_dir/"first_reached.npy", np.array(first80))
print("HH done  →", data_dir)
