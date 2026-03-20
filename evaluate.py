"""
evaluate.py — Fixed evaluator. DO NOT MODIFY.

Usage:
    python3 evaluate.py            # full run (300 gens)
    python3 evaluate.py --quick    # fast sanity check (50 gens)
"""
import argparse
import csv
import importlib.util
import json
import subprocess
from pathlib import Path

import numpy as np

# ── Paths ────────────────────────────────────────────────────────────────────
MODEL_FILE   = Path("model.py")
PARAMS_FILE  = Path("parameters.csv")
SPECS_FILE   = Path("specs.json")
RESULTS_FILE = Path("results.tsv")
BEST_FILE    = Path("best_parameters.json")


# ── Load project files ───────────────────────────────────────────────────────
def _load_params():
    defs = []
    with open(PARAMS_FILE) as f:
        for row in csv.DictReader(f):
            d = {"name": row["name"], "min": float(row["min"]),
                 "max": float(row["max"]), "scale": row["scale"].strip()}
            if d["scale"] == "log":
                d["log_min"] = np.log10(d["min"])
                d["log_max"] = np.log10(d["max"])
            defs.append(d)
    return defs


def _load_model():
    spec = importlib.util.spec_from_file_location("model", MODEL_FILE)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.run_model


def _vec_to_params(x, defs):
    p = {}
    for i, d in enumerate(defs):
        v = x[i]
        if d["scale"] == "log":
            v = 10 ** (d["log_min"] + v * (d["log_max"] - d["log_min"]))
        else:
            v = d["min"] + v * (d["max"] - d["min"])
        p[d["name"]] = v
    return p


def _cost(x, model_fn, defs, specs):
    try:
        metrics = model_fn(_vec_to_params(x, defs))
    except Exception:
        return 1e9
    c = 0.0
    for key, target in specs.items():
        v   = metrics.get(key, 0.0)
        rel = (v - target) / max(abs(target), 1e-30)
        c  += rel * rel
    return c


# ── Differential Evolution ───────────────────────────────────────────────────
def _de(model_fn, defs, specs, pop=60, gens=300, F=0.8, CR=0.9, seed=42):
    rng = np.random.default_rng(seed)
    n   = len(defs)
    population = rng.random((pop, n))
    fitness    = np.array([_cost(population[i], model_fn, defs, specs) for i in range(pop)])

    for gen in range(gens):
        for i in range(pop):
            candidates = [j for j in range(pop) if j != i]
            a, b, c    = rng.choice(candidates, 3, replace=False)
            mutant     = np.clip(population[a] + F * (population[b] - population[c]), 0.0, 1.0)
            cross      = rng.random(n) < CR
            trial      = np.where(cross, mutant, population[i])
            tc         = _cost(trial, model_fn, defs, specs)
            if tc < fitness[i]:
                population[i] = trial
                fitness[i]    = tc

        if gen % 50 == 0 or gen == gens - 1:
            best_i   = int(np.argmin(fitness))
            best_p   = _vec_to_params(population[best_i], defs)
            metrics  = model_fn(best_p)
            row      = {k: f"{v:.4g}" for k, v in metrics.items()}
            print(f"  gen {gen:4d}  cost={fitness[best_i]:.6f}  {row}")

    best_i = int(np.argmin(fitness))
    return _vec_to_params(population[best_i], defs), float(fitness[best_i])


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="50-gen sanity check")
    args = parser.parse_args()

    defs    = _load_params()
    specs   = json.loads(SPECS_FILE.read_text())
    model_fn = _load_model()
    gens    = 50 if args.quick else 300

    print(f"\n{'='*60}")
    print(f"  autoresearch evaluator  {len(defs)} params, pop=60, gens={gens}")
    print(f"{'='*60}\n")

    best_params, best_cost = _de(model_fn, defs, specs, gens=gens)
    metrics = model_fn(best_params)

    print(f"\n{'-'*60}")
    print("  BEST PARAMETERS")
    for k, v in best_params.items():
        print(f"    {k:15s} = {v:.6g}")

    print(f"\n  METRICS vs SPECS")
    n_met = 0
    for key, target in specs.items():
        v   = metrics.get(key, 0.0)
        err = abs(v - target) / max(abs(target), 1e-30) * 100
        ok  = "OK" if err < 5 else "XX"
        print(f"    {ok} {key:15s}  got={v:.4g}  target={target:.4g}  err={err:.1f}%")
        if err < 5:
            n_met += 1
    score = n_met / len(specs)
    print(f"\n  Score: {n_met}/{len(specs)} ({score*100:.0f}%)   cost={best_cost:.6f}")
    print(f"{'='*60}\n")

    BEST_FILE.write_text(json.dumps(best_params, indent=2))

    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        commit = "unknown"

    with open(RESULTS_FILE, "a") as f:
        f.write(f"{commit}\t{score:.3f}\t{best_cost:.6f}\t{json.dumps(best_params)}\n")


if __name__ == "__main__":
    main()
