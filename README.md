# PFAS Closed-Loop Nanobiosensor — Autonomous Design

> **Status:** 🔧 In Progress — initial topology committed, evaluation pending

---

## What This Is

An autonomous bioelectronic nanomicrosystem design experiment.
A research agent iteratively designs, optimizes, and validates a **closed-loop implantable PFAS nanobiosensor** until all 7 performance specs are simultaneously met within ±5%.

The agent runs full physics-based ODE simulation, evaluates metrics against targets, diagnoses failures, redesigns the model topology, and repeats — committing every iteration to git.

---

## Why This Is Hard

7 specs that **compete and conflict**:

| Conflict | Specs involved |
|----------|---------------|
| High peak + low final | `y_peak` vs `y_final` — needs strong transient AND strong inhibition |
| Fast rise + controlled timing | `rise_time` vs `t_peak` — binding can't be too fast or too slow |
| Specific decay + specific undershoot | `decay` vs `undershoot` — damping must be precisely tuned |
| Undershoot + settling time | `undershoot` vs `t_settle` — must dip below baseline, then recover by t=14 |
| Large overshoot ratio (7×) | `y_peak / y_final = 7` — requires strong transient suppression mechanism |

No simple 2-state model can satisfy all 7. The agent must discover the right topology.

---

## Target Specs (all must be within ±5%)

| Metric | Target | What it measures |
|--------|--------|-----------------|
| `y_peak` | **7.0** | Peak electrochemical output amplitude |
| `y_final` | **1.0** | Stable steady-state baseline |
| `decay` | **0.4** | Exponential decay rate constant after peak |
| `t_peak` | **5.0** | Time at which peak occurs |
| `rise_time` | **2.5** | Time from 10% → 90% of peak (rising edge) |
| `t_settle` | **14.0** | Last time output exits ±5% band around y_final |
| `undershoot` | **0.7** | Minimum output after peak (nadir before recovery) |

---

## Required Response Shape

```
y(t)
 7 │              ●  ← y_peak = 7.0   (t_peak = 5.0)
   │           ╱   ╲
   │         ╱       ╲  decay = 0.4
   │       ╱           ╲
   │     ╱               ╲___________
 1 │   ╱                             ●●● ← y_final = 1.0
   │  ╱                ╲__●__╱           ← undershoot = 0.7 (dips before recovering)
   │◄──────────────────────────────────►
   0  ←rise_time=2.5→       t_settle=14
```

Key shape requirements:
- **Fast asymmetric rise**: 10%→90% in 2.5 time units
- **Precise peak timing**: must peak exactly at t = 5.0
- **Controlled decay**: initial fall rate = 0.4/time
- **Undershoot nadir**: dips to 0.7 before recovering to 1.0
- **Settled by t=14**: within ±5% of y_final and stays there

---

## System Architecture (Current Topology)

```
[PFAS analyte input — step at t=0]
         │
         ▼
┌─────────────────────────┐
│  Nanosensor  s(t)       │  Langmuir binding, fast inhibition + slow adaptation
│  ds/dt = k_bind(1-s)    │
│        - k_des·s        │ ◄─── k_inh·y·s   (fast output feedback)
│        - k_inh·y·s      │ ◄─── k_adapt·h·s (slow adaptation feedback)
│        - k_adapt·h·s    │
└────────────┬────────────┘
             │ surface occupancy
             ▼
┌─────────────────────────┐
│  Microfluidic  m(t)     │  Buffered transport and signal amplification
│  dm/dt = k_trans·s      │
│        - k_rel·m        │
└────────────┬────────────┘
             │ transport signal
             ▼
┌─────────────────────────┐          ┌──────────────────────────┐
│  Output  y(t)           │─────────►│  Slow Adaptor  h(t)      │
│  dy/dt = k_gain·m       │          │  dh/dt = k_h_on·y        │
│        - k_fb·y         │          │        - k_h_off·h       │
└─────────────────────────┘          └──────────┬───────────────┘
         ▲                                       │ slow inhibition
         │                                       ▼
         └───────────────────────────── k_adapt·h·s ──────────────►
```

### ODEs

```
ds/dt = k_bind·(1−s) − k_des·s − k_inh·y·s − k_adapt·h·s
dm/dt = k_trans·s − k_rel·m
dy/dt = k_gain·m − k_fb·y
dh/dt = k_h_on·y − k_h_off·h
```

### Why This Topology

| Mechanism | Purpose | Spec it targets |
|-----------|---------|----------------|
| Fast binding burst | large initial y | `y_peak`, `rise_time` |
| Transport delay (m) | spreads peak timing | `t_peak` |
| Fast inhibition `k_inh·y·s` | drives peak down | `decay`, `y_final` |
| Slow adaptation `k_adapt·h·s` | oversuppresses sensor → undershoot | `undershoot` |
| Slow adaptation recovery `k_h_off` | h decays → y recovers | `t_settle` |
| Nonlinear steady state | y_final ≠ 0 | `y_final` |

The **4th state h** (slow adaptation / receptor desensitization) is what makes the undershoot spec possible. Without it, the 3-state system cannot dip below y_final.

---

## Parameters Being Optimized

| Parameter | Role | Scale | Range |
|-----------|------|-------|-------|
| `k_bind` | PFAS adsorption rate | log | 0.5 – 50 |
| `k_des` | Desorption / regeneration | log | 0.01 – 5 |
| `k_inh` | Fast output→sensor inhibition | log | 0.01 – 20 |
| `k_adapt` | Slow adaptation coupling | log | 0.01 – 20 |
| `k_trans` | Sensor→microfluidic coupling | log | 0.5 – 100 |
| `k_rel` | Microfluidic relaxation | log | 0.1 – 20 |
| `k_gain` | Electrochemical gain | log | 0.1 – 200 |
| `k_fb` | Adaptive feedback decay | log | 0.1 – 20 |
| `k_h_on` | Adaptation activation rate | log | 0.01 – 10 |
| `k_h_off` | Adaptation recovery rate | log | 0.005 – 2 |
| `T_end` | Simulation window | linear | 20 – 80 |

**Optimizer:** Differential Evolution (pop=60, gens=300, F=0.8, CR=0.9)

---

## Current Results

> ⏳ Not yet evaluated.

| Metric | Got | Target | Error | Status |
|--------|-----|--------|-------|--------|
| `y_peak` | — | 7.0 | — | ⏳ |
| `y_final` | — | 1.0 | — | ⏳ |
| `decay` | — | 0.4 | — | ⏳ |
| `t_peak` | — | 5.0 | — | ⏳ |
| `rise_time` | — | 2.5 | — | ⏳ |
| `t_settle` | — | 14.0 | — | ⏳ |
| `undershoot` | — | 0.7 | — | ⏳ |

**Score: 0/7**

---

## Iteration Log

| # | Commit | Score | Cost | What Changed | Why |
|---|--------|-------|------|--------------|-----|
| 1 | (pending) | 0/7 | — | Initial 4-state topology with slow adaptation | baseline design |

---

## How the Agent Iterates

```
┌─────────────────────────────────────────────────────────┐
│  1. python evaluate.py --quick   (50 gen sanity check)  │
│  2. python evaluate.py           (300 gen full run)     │
│  3. Read output — which specs are OK / XX?              │
│  4. Diagnose physical failure mode                      │
│  5. Modify model.py and/or parameters.csv               │
│  6. Update README.md (results table + iteration log)    │
│  7. git commit -m "topology: <what changed>"            │
│  8. Repeat until all 7 specs are OK                     │
└─────────────────────────────────────────────────────────┘
```

**Done when:** all 7 metrics within ±5% → commit `SOLVED | <description>`

---

## Files

| File | Role | Editable by agent |
|------|------|:-----------------:|
| `model.py` | Physics ODEs + metric computation | ✅ |
| `parameters.csv` | Parameter search ranges | ✅ |
| `README.md` | This file — live status dashboard | ✅ |
| `evaluate.py` | Optimization harness (DE) | ❌ |
| `specs.json` | Target metrics | ❌ |
| `best_parameters.json` | Best found parameters (auto) | — |
| `results.tsv` | Full experiment log (auto) | — |
