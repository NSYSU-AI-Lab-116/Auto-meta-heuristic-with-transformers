import numpy as np
from pathlib import Path
from scipy.stats import wilcoxon

data_dir = Path("research_workspace/auto-metaheuristic/exp_result/hh_result/data")
load = lambda n: np.load(data_dir / n) if (data_dir / n).exists() else None

hh_curves  = load("all_curves.npy")
hh_first80 = load("first_reached.npy")

de_curves  = load("de_curves.npy")
de_first80 = load("de_first_reached.npy")

ga_curves  = load("ga_curves.npy")
ga_first80 = load("ga_first_reached.npy")

pso_curves  = load("pso_curves.npy")
pso_first80 = load("pso_first_reached.npy")

hh_final  = hh_curves[:,-1]          if hh_curves  is not None else None
de_final  = de_curves[:,-1]          if de_curves  is not None else load("de_final.npy")
ga_final  = ga_curves[:,-1]          if ga_curves  is not None else load("ga_final.npy")
pso_final = pso_curves[:,-1]         if pso_curves is not None else load("pso_final.npy")

if hh_curves is None or hh_first80 is None or de_final is None:
    raise RuntimeError("missing required result files")

def p(a,b):
    n = min(len(a),len(b))
    return wilcoxon(a[:n],b[:n]).pvalue

p_de  = p(hh_final,de_final)
p_ga  = p(hh_final,ga_final)  if ga_final  is not None else None
p_pso = p(hh_final,pso_final) if pso_final is not None else None

rows = [
    ("Proposed HH",
     f"{hh_final.mean():.3e} ± {hh_final.std():.1e}",
     int(hh_first80.mean()),
     f"{p_de:.3g}",
     f"{p_ga:.3g}"  if p_ga  is not None else "—",
     f"{p_pso:.3g}" if p_pso is not None else "—")
]

rows.append(("DE",
             f"{de_final.mean():.3e} ± {de_final.std():.1e}",
             int(de_first80.mean()) if de_first80 is not None else "—",
             "–","–","–"))

if ga_final is not None:
    rows.append(("GA",
                 f"{ga_final.mean():.3e} ± {ga_final.std():.1e}",
                 int(ga_first80.mean()) if ga_first80 is not None else "—",
                 "–","–","–"))

if pso_final is not None:
    rows.append(("PSO",
                 f"{pso_final.mean():.3e} ± {pso_final.std():.1e}",
                 int(pso_first80.mean()) if pso_first80 is not None else "—",
                 "–","–","–"))

header = f"{'Method':<10} {'Final best (mean±std)':<28} {'Eval@80%':<9} {'p-DE':<8} {'p-GA':<8} {'p-PSO':<8}"
lines  = [header] + [f"{m:<10} {f:<28} {e:<9} {p1:<8} {p2:<8} {p3:<8}"
                     for m,f,e,p1,p2,p3 in rows]

for l in lines:
    print(l)

out_dir  = Path("research_workspace/auto-metaheuristic/exp_result/all_runner")
out_dir.mkdir(parents=True, exist_ok=True)
with open(out_dir / "stats_table.txt","w",encoding="utf-8") as f:
    f.write("\n".join(lines))
