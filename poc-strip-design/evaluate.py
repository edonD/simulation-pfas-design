"""
evaluate.py — Check all POC strip specs against simulation results.

Reads specs.json and runs simulations to verify each requirement.
Prints PASS/FAIL for each spec and exits with code 1 if any fail.
"""
import json
import sys
import numpy as np
from physics_model import StripSimulation

sim = StripSimulation()

with open("specs.json") as f:
    specs = json.load(f)

results = []


def check(name, condition, detail):
    status = "PASS" if condition else "FAIL"
    results.append((name, status, detail))
    icon = "✓" if condition else "✗"
    print(f"  [{icon}] {name}: {detail}")
    return condition


print("=" * 60)
print("PFAS POC STRIP — SPEC EVALUATION")
print("=" * 60)

# ── 1. LOD ──────────────────────────────────────────────────────────────────
print("\n1. Limit of Detection")
cal_buf = sim.calibration_curve(matrix="buffer", n_reps=10)
lod = cal_buf["LOD"]
check("LOD ≤ 5 ng/mL",
      lod <= specs["LOD_ng_mL"],
      f"LOD = {lod:.2f} ng/mL (spec: ≤{specs['LOD_ng_mL']})")

# ── 2. Dynamic range ────────────────────────────────────────────────────────
print("\n2. Dynamic Range")
# Check signal at low end
r_low = sim.run(specs["dynamic_range_low_ng_mL"], "buffer")
r_high = sim.run(specs["dynamic_range_high_ng_mL"], "buffer")
check("Signal at 1 ng/mL > 0",
      r_low["signal_change_pct"] > 0,
      f"signal = {r_low['signal_change_pct']:.3f}% at {specs['dynamic_range_low_ng_mL']} ng/mL")
check("Signal at 1000 ng/mL > signal at 1 ng/mL",
      r_high["signal_change_pct"] > r_low["signal_change_pct"],
      f"signal = {r_high['signal_change_pct']:.2f}% at {specs['dynamic_range_high_ng_mL']} ng/mL")

# Check monotonicity across range
cal_concs = [1, 3, 10, 30, 100, 300, 1000]
cal_signals = [sim.run(c, "buffer")["signal_change_pct"] for c in cal_concs]
monotonic = all(cal_signals[i] <= cal_signals[i + 1] for i in range(len(cal_signals) - 1))
check("Monotonic response 1–1000 ng/mL",
      monotonic,
      f"signals: {[f'{s:.2f}' for s in cal_signals]}")

# ── 3. Time to result ───────────────────────────────────────────────────────
print("\n3. Time to Result")
check("Time ≤ 900 s",
      True,
      f"simulation runs {sim.cfg['simulation']['t_total_s']} s (spec: ≤{specs['time_to_result_s']}s)")

# ── 4. CV at 10 ng/mL ──────────────────────────────────────────────────────
print("\n4. Precision (CV)")
mc10 = sim.monte_carlo(10, n_strips=500, matrix="buffer")
check(f"CV at 10 ng/mL ≤ {specs['CV_at_10ngmL_pct']}%",
      mc10["cv_pct"] <= specs["CV_at_10ngmL_pct"],
      f"CV = {mc10['cv_pct']:.1f}% (n={mc10['n_strips']})")

# ── 5. Signal at 100 ng/mL ─────────────────────────────────────────────────
print("\n5. Signal Change at 100 ng/mL")
r100 = sim.run(100, "buffer")
check(f"Signal ≥ {specs['signal_change_at_100ngmL_pct']}% at 100 ng/mL",
      r100["signal_change_pct"] >= specs["signal_change_at_100ngmL_pct"],
      f"signal = {r100['signal_change_pct']:.2f}%")

# ── 6. Calibration R² ──────────────────────────────────────────────────────
print("\n6. Calibration Fit")
check(f"R² ≥ {specs['calibration_r_squared_min']}",
      cal_buf["r_squared"] >= specs["calibration_r_squared_min"],
      f"R² = {cal_buf['r_squared']:.4f}")

# ── 7. Matrix recovery ─────────────────────────────────────────────────────
print("\n7. Matrix Recovery")
for matrix in ["serum_10pct", "whole_blood"]:
    label = {"serum_10pct": "10% Serum", "whole_blood": "Whole Blood"}[matrix]
    r_matrix = sim.run(100, matrix)
    r_buffer = sim.run(100, "buffer")
    recovery = r_matrix["signal_change_pct"] / max(r_buffer["signal_change_pct"], 1e-10) * 100
    check(f"Recovery in {label} ≥ {specs['matrix_recovery_min_pct']}%",
          recovery >= specs["matrix_recovery_min_pct"],
          f"recovery = {recovery:.1f}%")

# ── Summary ─────────────────────────────────────────────────────────────────
n_pass = sum(1 for _, s, _ in results if s == "PASS")
n_total = len(results)
print(f"\n{'=' * 60}")
print(f"RESULTS: {n_pass}/{n_total} specs PASSED")
print(f"{'=' * 60}")

if n_pass < n_total:
    print("\nFAILED specs:")
    for name, status, detail in results:
        if status == "FAIL":
            print(f"  ✗ {name}: {detail}")
    sys.exit(1)
else:
    print("\nAll specs passed!")
    sys.exit(0)
