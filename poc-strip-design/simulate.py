#!/usr/bin/env python3
"""simulate.py — Run full PFAS POC strip simulation and generate 5 diagnostic plots.

Plots:
  1. Time traces (PFOS release, transport, binding, current)
  2. Calibration curves for buffer, serum, whole_blood
  3. Sensitivity tornado chart
  4. Monte Carlo histograms
  5. SWV voltammograms
"""
import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from physics_model import StripSimulation

OUT_DIR = "plots"
os.makedirs(OUT_DIR, exist_ok=True)

sim = StripSimulation()
cfg = sim.cfg

MATRICES = ["buffer", "serum_10pct", "whole_blood"]
MATRIX_LABELS = {"buffer": "Buffer", "serum_10pct": "10% Serum", "whole_blood": "Whole Blood"}
MATRIX_COLORS = {"buffer": "#1f77b4", "serum_10pct": "#ff7f0e", "whole_blood": "#d62728"}


def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {path}")


# ── Plot 1: Time traces (multiple concentrations in buffer) ──────────────────
print("1. Time traces ...")
concentrations = [0.1, 1, 10, 100, 1000]
colors_conc = plt.cm.viridis(np.linspace(0.1, 0.9, len(concentrations)))

fig, axes = plt.subplots(2, 2, figsize=(12, 9))
for c, col in zip(concentrations, colors_conc):
    r = sim.run(c, "buffer")
    label = f"{c} ng/mL"
    axes[0, 0].plot(r["t"], np.array(r["c_free_t"]) * 1e9, color=col, label=label)
    axes[0, 1].plot(r["t"], np.array(r["c_electrode_t"]) * 1e9, color=col, label=label)
    axes[1, 0].plot(r["t"], r["theta_effective_t"], color=col, label=label)
    axes[1, 1].plot(r["t"], r["i_peak_t"], color=col, label=label)

axes[0, 0].set_ylabel("Free [PFOS] (nM)")
axes[0, 0].set_title("Stage 1: PFOS Release")
axes[0, 1].set_ylabel("[PFOS] at Electrode (nM)")
axes[0, 1].set_title("Stage 2: Capillary Transport")
axes[1, 0].set_ylabel("MIP Coverage (θ)")
axes[1, 0].set_title("Stage 3: MIP Binding Kinetics")
axes[1, 1].set_ylabel("Peak Current (µA)")
axes[1, 1].set_title("Stage 4: SWV Signal")

for ax in axes.flat:
    ax.set_xlabel("Time (s)")
    ax.legend(fontsize=7, loc="best")
    ax.grid(True, alpha=0.3)

fig.suptitle("PFAS Test Strip — Time-Resolved Physics (Buffer)", fontsize=14, fontweight="bold")
fig.tight_layout()
save(fig, "01_time_traces.png")


# ── Plot 2: Calibration curves (buffer, serum, blood) ────────────────────────
print("2. Calibration curves ...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

cal_results = {}
for mx in MATRICES:
    cal = sim.calibration_curve(matrix=mx, n_reps=5)
    cal_results[mx] = cal
    concs = np.array(cal["concentrations"])
    means = np.array(cal["means"])
    stds = np.array(cal["stds"])
    col = MATRIX_COLORS[mx]
    lbl = f"{MATRIX_LABELS[mx]} (LOD={cal['LOD']:.1f}, R²={cal['r_squared']:.3f})"

    mask = concs > 0
    ax1.errorbar(concs[mask], means[mask], yerr=stds[mask], fmt="o-",
                 color=col, capsize=3, label=lbl, markersize=4)
    ax2.errorbar(concs[mask], means[mask], yerr=stds[mask], fmt="o-",
                 color=col, capsize=3, label=lbl, markersize=4)

    if cal["fit_success"]:
        x_fit = np.logspace(np.log10(0.05), np.log10(1200), 200)
        y_fit = cal["S_max"] * x_fit / (cal["Kd_app"] + x_fit)
        ax1.plot(x_fit, y_fit, "--", color=col, alpha=0.5)
        ax2.plot(x_fit, y_fit, "--", color=col, alpha=0.5)

ax1.axvline(cal_results["buffer"]["LOD"], color="#1f77b4", ls=":", alpha=0.5,
            label=f"Buffer LOD = {cal_results['buffer']['LOD']:.1f} ng/mL")
ax1.set_xscale("log")
ax1.set_xlabel("[PFOS] (ng/mL)")
ax1.set_ylabel("Signal Change (%)")
ax1.set_title("Calibration (log scale)")
ax1.legend(fontsize=7)
ax1.grid(True, alpha=0.3)

ax2.set_xlabel("[PFOS] (ng/mL)")
ax2.set_ylabel("Signal Change (%)")
ax2.set_title("Calibration (linear scale)")
ax2.legend(fontsize=7)
ax2.grid(True, alpha=0.3)

fig.suptitle("PFAS Test Strip — Multi-Matrix Calibration", fontsize=14, fontweight="bold")
fig.tight_layout()
save(fig, "02_calibration_curves.png")


# ── Plot 3: Sensitivity tornado ──────────────────────────────────────────────
print("3. Sensitivity tornado ...")
sa = sim.sensitivity_analysis(c_PFOS_ng_mL=10.0, matrix="buffer")

params = sorted(sa.keys(), key=lambda k: abs(sa[k]["elasticity"]))
elasticities = [sa[p]["elasticity"] for p in params]

fig, ax = plt.subplots(figsize=(10, 6))
y_pos = np.arange(len(params))
bar_colors = ["#2ca02c" if e > 0 else "#d62728" for e in elasticities]
ax.barh(y_pos, elasticities, color=bar_colors, height=0.6, edgecolor="black", linewidth=0.5)
ax.set_yticks(y_pos)
ax.set_yticklabels(params)
ax.set_xlabel("Elasticity: Δ(Signal%) / Signal% for ±50% parameter change")
ax.set_title("Sensitivity Analysis — 10 ng/mL PFOS in Buffer", fontweight="bold")
ax.axvline(0, color="black", lw=0.8)
ax.grid(axis="x", alpha=0.3)

for i, e in enumerate(elasticities):
    ax.text(e + 0.01 * np.sign(e), i, f"{e:.2f}", va="center", fontsize=8)

fig.tight_layout()
save(fig, "03_sensitivity_tornado.png")


# ── Plot 4: Monte Carlo histograms ───────────────────────────────────────────
print("4. Monte Carlo histograms ...")
mc_concs = [1, 10, 100]
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ax, c in zip(axes, mc_concs):
    mc = sim.monte_carlo(c, n_strips=500, matrix="buffer")
    ax.hist(mc["signals"], bins=30, color="steelblue", edgecolor="white", alpha=0.85,
            density=True)
    ax.axvline(mc["mean"], color="red", ls="--", lw=2,
               label=f"Mean = {mc['mean']:.2f}%")
    ax.axvline(mc["mean"] - mc["std"], color="orange", ls=":", lw=1.5)
    ax.axvline(mc["mean"] + mc["std"], color="orange", ls=":", lw=1.5,
               label=f"±1σ (CV = {mc['cv_pct']:.1f}%)")
    ax.set_xlabel("Signal Change (%)")
    ax.set_ylabel("Probability Density")
    ax.set_title(f"[PFOS] = {c} ng/mL")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

fig.suptitle("Monte Carlo — Strip-to-Strip Variability (N=500, Buffer)",
             fontsize=14, fontweight="bold")
fig.tight_layout()
save(fig, "04_monte_carlo.png")


# ── Plot 5: SWV voltammograms ────────────────────────────────────────────────
print("5. SWV voltammograms ...")
fig, ax = plt.subplots(figsize=(9, 6))

swv_concs = [0, 1, 10, 100, 1000]
colors_swv = plt.cm.plasma(np.linspace(0.1, 0.9, len(swv_concs)))

for c, col in zip(swv_concs, colors_swv):
    r = sim.run(c, "buffer")
    label = f"Blank (0 ng/mL)" if c == 0 else f"{c} ng/mL ({r['signal_change_pct']:.1f}%)"
    ax.plot(r["E_range"], r["i_swv"], color=col, label=label, linewidth=1.5)

ax.axvline(0.70, color="gray", linestyle=":", alpha=0.5, label="E° TEMPO (0.70 V)")
ax.set_xlabel("Potential (V vs Ag/AgCl)")
ax.set_ylabel("SWV Current (µA)")
ax.set_title("Square-Wave Voltammograms — TEMPO-MIP Electrode", fontweight="bold")
ax.legend()
ax.grid(True, alpha=0.3)

fig.tight_layout()
save(fig, "05_swv_voltammograms.png")


# ── Summary ──────────────────────────────────────────────────────────────────
print("\n=== SIMULATION SUMMARY ===")
for mx in MATRICES:
    cal = cal_results[mx]
    print(f"\n{MATRIX_LABELS[mx]}:")
    print(f"  LOD:       {cal['LOD']:.2f} ng/mL")
    print(f"  R²:        {cal['r_squared']:.4f}")
    print(f"  S_max:     {cal['S_max']:.2f}%")
    print(f"  Kd_app:    {cal['Kd_app']:.1f} ng/mL")
    print(f"  σ_blank:   {cal['sigma_blank']:.4f}%")

mc10 = sim.monte_carlo(10, n_strips=500, matrix="buffer")
print(f"\nMonte Carlo @ 10 ng/mL (buffer): CV = {mc10['cv_pct']:.1f}%")

r100 = sim.run(100, "buffer")
print(f"Signal @ 100 ng/mL buffer: {r100['signal_change_pct']:.2f}%")
print("\nAll 5 plots saved to plots/")
