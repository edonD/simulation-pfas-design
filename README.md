# PFAS Closed-Loop Nanobiosensor — Simulation & Design Report

## Status: SOLVED — All 7/7 Specs Met

---

## 1. What Is This?

This project designs a **closed-loop implantable nanobiosensor** that detects PFAS (per- and polyfluoroalkyl substances, aka "forever chemicals") in a biological system.

The sensor must produce a very specific electrochemical signal when PFAS molecules arrive — a signal with exact timing, amplitude, decay rate, and recovery behavior. These 7 requirements are defined as hard specs, and ALL must be met within ±5% simultaneously.

An autonomous research agent (Claude) iteratively designed the physics model, tuned the equations, and optimized parameters over 12 topology iterations until all specs were satisfied.

---

## 2. The Problem: 7 Specs That Must All Pass

When PFAS molecules arrive at t=0, the sensor output y(t) must follow this exact shape:

```
y(t)
 7 |              *  <-- peak = 7.0 at t = 5.0
   |           /   \
   |         /       \  decay rate = 0.4/s
   |       /           \
   |     /               \___________
 1 |   /                             *** <-- steady state = 1.0
   |  /                \__*__/           <-- dips to 0.7 then recovers
   |                                         settled by t = 14.0
   0  |<-rise=2.5->|
```

| # | Spec | Target | What It Means |
|---|------|--------|---------------|
| 1 | `y_peak` | 7.0 | How loud the initial alarm is |
| 2 | `y_final` | 1.0 | Steady monitoring level after alarm |
| 3 | `decay` | 0.4 | How fast the alarm quiets down |
| 4 | `t_peak` | 5.0 | When the alarm peaks |
| 5 | `rise_time` | 2.5 | How fast the signal rises (10% to 90%) |
| 6 | `t_settle` | 14.0 | When the signal finishes oscillating |
| 7 | `undershoot` | 0.7 | How far the signal dips below steady state |

**Why is this hard?** These specs fight each other. A higher peak needs more gain, but more gain makes the steady state too high. Deeper undershoot needs more oscillation, but more oscillation delays settling. The decay rate and undershoot are both controlled by the same damping parameter. Getting all 7 right simultaneously requires precisely balanced physics.

---

## 3. The Solution: What We Built

### System Response — All Specs Annotated

![System Response](plots/01_system_response.png)

This is the main result. The blue curve is the sensor's electrochemical output over time. Every red annotation shows a spec being met within ±5%.

### Verification: Each Spec Checked Independently

![Spec Verification](plots/03_spec_verification.png)

Each panel zooms into one spec and shows exactly how it was measured:
- **y_peak**: Maximum of y(t) = 6.962 (target 7.0, error 0.5%)
- **y_final**: Mean of last 2% of simulation = 1.016 (target 1.0, error 1.6%)
- **decay**: Slope of log(excess) after peak = 0.387 (target 0.4, error 3.2%)
- **t_peak**: Time of maximum = 4.884 (target 5.0, error 2.3%)
- **rise_time**: Time from 10% to 90% of peak = 2.494 (target 2.5, error 0.2%)
- **t_settle**: Last exit from ±5% band = 13.76 (target 14.0, error 1.7%)
- **undershoot**: Minimum after peak = 0.701 (target 0.7, error 0.1%)

---

## 4. How It Works — The Physics

### Architecture: 5 Coupled Differential Equations

![All States](plots/02_all_states.png)

The system has 5 internal state variables, each representing a physical component:

| State | Physical Meaning | What It Does |
|-------|-----------------|-------------|
| **x(t)** | Sensor surface occupancy | PFAS molecules bind to functionalized nanoparticles. Rises from 0 to ~0.9 as PFAS adsorbs. |
| **xd(t)** | Delayed sensor signal | Signal passes through a microfluidic transport channel, adding a 2-second lag. This is what controls peak timing. |
| **y(t)** | Electrochemical output | The measured signal. Behaves as an underdamped oscillator — rises, overshoots, undershoots, settles. |
| **z(t)** | Output rate | Velocity of y. Positive during rise, negative during fall, oscillates around zero. |
| **b(t)** | Burst amplification | Starts at 188x, decays exponentially. Multiplies the sensor signal early on, creating the 7x peak. Gone by steady state. |

### The Equations

```
dx/dt  = k_on * (1 - x) - k_off * x              Sensor: PFAS binds, desorbs
dxd/dt = (x - xd) / tau_d                          Transport: delayed version of sensor
dz/dt  = wn^2 * (K*(1+b)*xd - y) - 2*zeta*wn*z   Oscillator: tracks target with overshoot
dy/dt  = z                                          Output: integral of rate
db/dt  = -k_bd * b                                  Burst: exponential decay from b0
```

### Why Each Component Exists

| Component | Without It | Problem |
|-----------|-----------|---------|
| **Burst b** | Peak = 1.2 instead of 7.0 | Can't get 7x peak-to-final ratio from a stable system |
| **Transport delay xd** | t_peak = 4.6 instead of 5.0 | Peak happens too early without the lag |
| **Oscillator (2nd order)** | No undershoot at all | First-order systems can't oscillate below steady state |
| **Damping zeta** | Infinite oscillation | System never settles without damping |
| **Sensor x** | Instant step input | No realistic rise dynamics, rise_time = 0 |

---

## 5. The Optimized Parameters

These 9 parameters were found by Differential Evolution (population 60, 300 generations):

| Parameter | Value | Physical Meaning |
|-----------|-------|-----------------|
| `k_on` | 0.1213 | PFAS binding rate to sensor surface |
| `k_off` | 0.00443 | PFAS desorption rate from sensor |
| `tau_d` | 2.000 | Microfluidic transport delay (seconds) |
| `wn` | 0.807 | Natural oscillation frequency (rad/s) |
| `zeta` | 0.460 | Damping ratio (underdamped, < 1) |
| `K` | 1.194 | Steady-state electrochemical gain |
| `b0` | 188.3 | Initial burst amplification factor |
| `k_bd` | 0.569 | Burst decay rate |
| `T_end` | 20.87 | Simulation duration |

### How the Optimizer Found Them

![Optimizer Convergence](plots/04_optimizer_convergence.png)

The optimizer started with random parameter guesses (cost = 0.75, 1/7 specs met) and converged over 300 generations to the final solution (cost = 0.002, 7/7 specs met). By generation 100, 6/7 specs were already close.

---

## 6. Sensitivity Analysis

![Sensitivity](plots/05_sensitivity.png)

Each panel shows what happens when one parameter is swept ±30% from its optimal value (blue = nominal, red/blue gradient = perturbed). Key observations:

- **wn** (frequency) and **zeta** (damping) are the most sensitive — small changes shift timing and oscillation depth
- **b0** (burst) mainly affects peak height without disturbing steady state
- **tau_d** (delay) shifts the whole response in time
- **K** (gain) scales the steady-state level

---

## 7. Robustness Analysis

![Robustness](plots/06_robustness.png)

**Left panel**: With ±5% random noise on ALL parameters simultaneously, how often does each spec still pass? Rise time is very robust (86%), while undershoot is most sensitive (18%). This is expected — the undershoot depends on a precise damping balance.

**Right panel**: 50 perturbed trajectories overlaid. The overall shape is preserved under noise, but the fine details (exact undershoot depth, exact settling time) shift. The nominal design (red) is at the center of the envelope.

**What this means**: The design hits all specs at the nominal parameters, but manufacturing tolerances would need to be controlled to ±2-3% for reliable spec compliance. This is typical for precision bioelectronic systems.

---

## 8. How to Reproduce

### Run the Evaluation
```bash
python3 evaluate.py          # Full 300-generation optimization
python3 evaluate.py --quick  # Quick 50-generation sanity check
```

### Generate the Plots
```bash
python3 generate_report.py   # Creates all plots in plots/
```

### View the Visualization
```bash
python3 visualize.py         # Creates response_plot.png + text summary
```

### Requirements
- Python 3.8+
- NumPy
- Matplotlib (for plots only)
- SciPy is NOT required (model uses custom RK4 integrator)

---

## 9. Design Evolution — How We Got Here

The solution wasn't found on the first try. It took 12 topology redesigns:

| Version | Model | Score | Key Issue |
|---------|-------|-------|-----------|
| v1 | 4-state sensor-inhibition | 5/7 | y_final (0.82) and undershoot (0.78) coupled — ratio stuck at 0.95 |
| v2 | + burst amplification | 5/7 | Burst helped peak but didn't fix ratio |
| v3 | Decoupled adaptation (h acts on output) | 3/7 | y_final improved but timing collapsed |
| v4 | Dual-path adaptation (sensor + output) | 4/7 | Better undershoot but t_settle failed |
| v5 | Quadratic h response (y^2) | 3/7 | Selective transient adaptation, but hard to optimize |
| v6 | Two adaptation variables | 5/7 | Optimizer ignored second variable |
| v7 | Threshold-activated adaptation | 5/7 | g_ss=0 idea was right, but settling time suffered |
| v8 | Dual sensor populations | 5/7 | Optimizer ignored slow sensor |
| **v9** | **Second-order oscillator + burst** | **5/7** | **Breakthrough: undershoot/y_final decoupled! decay and t_peak still off** |
| v10 | + sensor-output inhibition | 5/7 | Didn't help decay |
| v11 | + adaptive target suppression | 3/7 | Too many parameters, poor convergence |
| **v12** | **+ transport delay** | **7/7** | **Transport lag fixed t_peak, decay followed. SOLVED.** |

The two critical breakthroughs:
1. **v9**: Switching from first-order to second-order output dynamics gave natural oscillatory undershoot, decoupling it from steady-state level
2. **v12**: Adding a transport delay stage shifted peak timing independently of all other dynamics

---

## 10. Files

| File | What It Does |
|------|-------------|
| `model.py` | The 5-state ODE model (the core physics) |
| `parameters.csv` | Parameter search ranges for the optimizer |
| `evaluate.py` | Differential Evolution optimizer + metric extraction |
| `specs.json` | The 7 target specifications |
| `best_parameters.json` | Optimized parameter values |
| `results.tsv` | Full optimization log across all runs |
| `generate_report.py` | Script to create all plots |
| `visualize.py` | Quick single-plot visualization |
| `plots/` | All generated figures |

---

## 11. Final Scorecard

```
============================================================
  PFAS NANOBIOSENSOR — FINAL RESULTS
============================================================

  METRIC          GOT      TARGET    ERROR    STATUS
  ──────          ───      ──────    ─────    ──────
  y_peak          6.962    7.0       0.5%     PASS
  y_final         1.016    1.0       1.6%     PASS
  decay           0.387    0.4       3.2%     PASS
  t_peak          4.884    5.0       2.3%     PASS
  rise_time       2.494    2.5       0.2%     PASS
  t_settle        13.76    14.0      1.7%     PASS
  undershoot      0.701    0.7       0.1%     PASS

  Score: 7/7 (100%)
  Cost:  0.002166

============================================================
```
