import numpy as np
from pathlib import Path
from src.python.Config import Configs
from src.python.Optimizer import Optimizers, HyperParameters

FUNC_TYPE, YEAR, NAME, DIM = "CEC", "2021", "F9", 10
ITER, TRIALS = 1500, 6

root = Path("research_workspace/auto-metaheuristic/exp_result")
data_dir = root / "hh_result" / "data"
data_dir.mkdir(parents=True, exist_ok=True)

obj_func = Configs.DataSet.get_function(FUNC_TYPE, YEAR, NAME, DIM)
GA = Optimizers.metaheuristic_list["GA"]

all_curves = []
for _ in range(TRIALS):
    _, curve = GA(ITER, HyperParameters.Parameters["num_individual"], obj_func).start()
    all_curves.append(curve)

all_curves = np.array(all_curves)
np.save(data_dir / "ga_curves.npy", all_curves)

first80 = []
for curve in all_curves:
    tgt = curve[-1] + 0.15 * (curve[0] - curve[-1])
    first80.append(next(i for i, v in enumerate(curve) if v <= tgt))
np.save(data_dir / "ga_first_reached.npy", np.array(first80))

np.save(data_dir / "ga_final.npy", all_curves[:, -1])
print("GA done →", data_dir)