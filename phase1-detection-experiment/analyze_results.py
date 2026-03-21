"""
analyze_results.py — Analyze Phase 1 PFOS detection experiment results.

After running the experiment, enter your measurements in data.csv and run:
    python3 analyze_results.py

Produces:
    results/calibration_curve.png
    results/summary.txt
"""
import os
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

os.makedirs("results", exist_ok=True)

DATA_FILE = "data.csv"

# ── Create template if data.csv doesn't exist ────────────────────────────────
if not os.path.exists(DATA_FILE):
    print(f"No {DATA_FILE} found. Creating template...")
    print(f"Fill in your measurements and run this script again.\n")

    with open(DATA_FILE, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(["concentration_ng_mL", "baseline_current_uA", "post_pfos_current_uA", "electrode_type", "notes"])
        # Example data (replace with your real measurements)
        w.writerow(["# Instructions:"])
        w.writerow(["# 1. Enter one row per measurement"])
        w.writerow(["# 2. concentration_ng_mL: PFOS concentration in ng/mL"])
        w.writerow(["# 3. baseline_current_uA: SWV peak current BEFORE PFOS exposure (microamps)"])
        w.writerow(["# 4. post_pfos_current_uA: SWV peak current AFTER PFOS exposure (microamps)"])
        w.writerow(["# 5. electrode_type: 'aptamer' or 'control' (no aptamer)"])
        w.writerow(["# 6. Delete these comment rows and the example data below before running"])
        w.writerow([])
        w.writerow(["# === EXAMPLE DATA (delete and replace with yours) ==="])
        # Example: 3 replicates per concentration
        for conc in [0, 0.01, 0.1, 1, 10, 100, 1000]:
            for rep in range(3):
                # Simulated data with noise
                rng = np.random.default_rng(42 + rep + int(conc * 100))
                baseline = 25.0 + rng.normal(0, 0.5)
                if conc > 0:
                    # Signal change roughly follows logistic
                    frac = 0.22 * conc / (conc + 5) + rng.normal(0, 0.01)
                    post = baseline * (1 - frac)
                else:
                    post = baseline + rng.normal(0, 0.3)
                w.writerow([conc, f"{baseline:.2f}", f"{post:.2f}", "aptamer", f"rep{rep+1}"])

        # Control electrodes (no aptamer)
        for rep in range(3):
            rng = np.random.default_rng(100 + rep)
            baseline = 25.0 + rng.normal(0, 0.5)
            post = baseline + rng.normal(0, 0.3)
            w.writerow([1000, f"{baseline:.2f}", f"{post:.2f}", "control", f"rep{rep+1}"])

    print(f"Template created: {DATA_FILE}")
    print(f"Edit it with your real data, then run: python3 {__file__}")
    exit(0)

# ── Load data ────────────────────────────────────────────────────────────────
print("Loading data...")
concs = []
signal_changes = []
ctrl_changes = []

with open(DATA_FILE) as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            # Skip comment rows
            if row.get("concentration_ng_mL", "").startswith("#") or not row.get("concentration_ng_mL", "").strip():
                continue
            conc = float(row["concentration_ng_mL"])
            baseline = float(row["baseline_current_uA"])
            post = float(row["post_pfos_current_uA"])
            etype = row.get("electrode_type", "aptamer").strip().lower()

            change_pct = (baseline - post) / baseline * 100

            if etype == "control":
                ctrl_changes.append(change_pct)
            else:
                concs.append(conc)
                signal_changes.append(change_pct)
        except (ValueError, KeyError):
            continue

concs = np.array(concs)
signal_changes = np.array(signal_changes)
ctrl_changes = np.array(ctrl_changes)

# ── Group by concentration ───────────────────────────────────────────────────
unique_concs = np.sort(np.unique(concs))
means = []
stds = []
for c in unique_concs:
    mask = concs == c
    vals = signal_changes[mask]
    means.append(np.mean(vals))
    stds.append(np.std(vals))

means = np.array(means)
stds = np.array(stds)

# ── Fit calibration curve ────────────────────────────────────────────────────
# Use logistic model: y = ymax * x / (Kd + x) + offset
def logistic(x, ymax, Kd, offset):
    return ymax * x / (Kd + x) + offset

try:
    positive_mask = unique_concs > 0
    popt, pcov = curve_fit(logistic, unique_concs[positive_mask], means[positive_mask],
                           p0=[20, 10, 0], maxfev=10000,
                           bounds=([0, 0.001, -10], [100, 10000, 10]))
    ymax, Kd, offset = popt
    fit_success = True
    print(f"Fit: ymax={ymax:.2f}%, Kd={Kd:.2f} ng/mL, offset={offset:.2f}%")
except Exception as e:
    print(f"Curve fit failed: {e}")
    fit_success = False

# ── Calculate LOD ────────────────────────────────────────────────────────────
# LOD = 3 * sigma_blank / slope_at_low_concentration
blank_mask = unique_concs == 0
if blank_mask.any():
    sigma_blank = stds[blank_mask][0]
else:
    sigma_blank = stds[0]  # use lowest conc std

if fit_success and Kd > 0:
    # Slope at low concentration = ymax / Kd
    slope = ymax / Kd
    LOD = 3 * sigma_blank / slope if slope > 0 else float('inf')
else:
    # Linear estimate from lowest two positive concentrations
    pos_concs = unique_concs[unique_concs > 0]
    pos_means = means[unique_concs > 0]
    if len(pos_concs) >= 2:
        slope = (pos_means[1] - pos_means[0]) / (pos_concs[1] - pos_concs[0])
        LOD = 3 * sigma_blank / slope if slope > 0 else float('inf')
    else:
        LOD = float('inf')

# ── Verdict ──────────────────────────────────────────────────────────────────
if LOD < 1:
    verdict = "EXCELLENT — Detects PFOS at general population blood levels. Strong path to product."
    verdict_color = "green"
elif LOD < 10:
    verdict = "GOOD — Detects PFOS in exposed populations. Viable with optimization."
    verdict_color = "orange"
elif LOD < 100:
    verdict = "MARGINAL — Only detects extreme exposure. Needs amplification or different approach."
    verdict_color = "red"
else:
    verdict = "FAILED — Cannot reliably detect PFOS. Try different aptamer, antibody, or EIS."
    verdict_color = "red"

# ── Plot calibration curve ───────────────────────────────────────────────────
print("Generating calibration curve...")
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Left: calibration curve
ax = axes[0]
ax.errorbar(unique_concs[unique_concs > 0], means[unique_concs > 0],
            yerr=stds[unique_concs > 0], fmt='bo', markersize=8, capsize=5,
            label='Aptamer electrodes')

if fit_success:
    x_fit = np.logspace(np.log10(max(0.001, unique_concs[unique_concs > 0].min())),
                        np.log10(unique_concs.max()), 200)
    y_fit = logistic(x_fit, *popt)
    ax.plot(x_fit, y_fit, 'b-', linewidth=2, alpha=0.5, label=f'Fit (Kd={Kd:.1f} ng/mL)')

# Control
if len(ctrl_changes) > 0:
    ctrl_mean = np.mean(ctrl_changes)
    ctrl_std = np.std(ctrl_changes)
    ax.axhspan(ctrl_mean - ctrl_std, ctrl_mean + ctrl_std, alpha=0.2, color='red', label='Control range')

# LOD line
if LOD < unique_concs.max():
    ax.axvline(x=LOD, color='green', linestyle='--', alpha=0.7, label=f'LOD = {LOD:.2f} ng/mL')

# Clinical reference lines
ax.axvline(x=2, color='orange', linestyle=':', alpha=0.4)
ax.text(2, ax.get_ylim()[1]*0.9, 'General\npopulation\n(2 ng/mL)', fontsize=7, color='orange', ha='left')
ax.axvline(x=20, color='red', linestyle=':', alpha=0.4)
ax.text(20, ax.get_ylim()[1]*0.9, 'High\nexposure\n(20 ng/mL)', fontsize=7, color='red', ha='left')

ax.set_xscale('log')
ax.set_xlabel('PFOS Concentration (ng/mL)', fontsize=12)
ax.set_ylabel('Signal Change (%)', fontsize=12)
ax.set_title('PFOS Calibration Curve', fontsize=13, fontweight='bold')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

# Right: verdict summary
ax2 = axes[1]
ax2.axis('off')
summary_text = f"""PHASE 1 RESULTS
{'='*40}

Limit of Detection:  {LOD:.2f} ng/mL

{'='*40}
VERDICT: {verdict}
{'='*40}

Calibration curve:
  Concentrations tested: {len(unique_concs)}
  Replicates per conc:   {len(concs)//len(unique_concs) if len(unique_concs) > 0 else 0}
  Max signal change:     {means.max():.1f}%
  Blank std dev:         {sigma_blank:.2f}%

Controls (no aptamer):
  N = {len(ctrl_changes)}
  Mean signal change: {np.mean(ctrl_changes):.2f}%
  (should be near 0%)

{'='*40}
NEXT STEPS:
"""
if LOD < 10:
    summary_text += """
  1. Test in spiked human serum
  2. Optimize incubation time
  3. Try multiple PFAS compounds
  4. Build disposable strip prototype
"""
else:
    summary_text += """
  1. Try EIS instead of SWV
  2. Try gold nanoparticle amplification
  3. Try different aptamer sequence
  4. Try antibody approach
"""

ax2.text(0.05, 0.95, summary_text, transform=ax2.transAxes,
         fontsize=10, fontfamily='monospace', verticalalignment='top',
         bbox=dict(facecolor='lightyellow', alpha=0.8, boxstyle='round'))

plt.tight_layout()
plt.savefig('results/calibration_curve.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"  Saved: results/calibration_curve.png")

# ── Save summary ─────────────────────────────────────────────────────────────
with open('results/summary.txt', 'w') as f:
    f.write(f"Phase 1 PFOS Detection Experiment Results\n")
    f.write(f"{'='*50}\n\n")
    f.write(f"Limit of Detection (LOD): {LOD:.4f} ng/mL\n")
    f.write(f"Verdict: {verdict}\n\n")
    f.write(f"Calibration data:\n")
    f.write(f"{'Conc (ng/mL)':>15} {'Mean Change (%)':>15} {'Std Dev (%)':>15}\n")
    for c, m, s in zip(unique_concs, means, stds):
        f.write(f"{c:>15.2f} {m:>15.2f} {s:>15.2f}\n")
    f.write(f"\nControl electrodes (no aptamer): mean change = {np.mean(ctrl_changes):.2f}% +/- {np.std(ctrl_changes):.2f}%\n")

print(f"  Saved: results/summary.txt")
print(f"\n{'='*50}")
print(f"  LOD = {LOD:.2f} ng/mL")
print(f"  {verdict}")
print(f"{'='*50}")
