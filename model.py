"""
model.py — Closed-Loop PFAS Nanobiosensor with Slow Adaptation

Architecture: 4-state bioelectronic nanomicrosystem for PFAS detection.

States:
    s  : nanosensor surface occupancy (PFAS capture, 0–1 normalized)
    m  : microfluidic transport / buffered signal intermediate
    y  : electrochemical output (measured signal)
    h  : slow adaptation variable (receptor desensitization / refractory state)

Physics:
    1. PFAS adsorbs to functionalized nanoparticle surface (s).
       Fast binding k_bind; fast desorption k_des.
    2. Surface occupancy drives microfluidic transport layer (m).
    3. Electrochemical output y rises with m and decays via adaptive feedback k_fb.
    4. Output y activates slow inhibitor h (receptor desensitization analog).
       h builds up slowly and inhibits the sensor surface (k_adapt).
    5. Once y peaks, h suppresses s → m drops → y drops below y_final (undershoot).
       h then decays slowly → s recovers → y returns to nonlinear steady state.

This 4-state topology produces:
    - Sharp transient peak (fast binding burst before inhibition)
    - Specific peak timing (transport delay sets t_peak)
    - Controlled post-peak decay (k_fb governs initial fall rate)
    - Undershoot below y_final (slow adaptation depresses sensor)
    - Eventual recovery to stable nonzero baseline (nonlinear equilibrium)

Metrics:
    y_peak     : peak output amplitude
    y_final    : steady-state output (mean of last 2% of simulation)
    decay      : exponential decay constant fitted immediately after peak
    t_peak     : time of peak occurrence
    rise_time  : time from 10% to 90% of y_peak (on the rising edge)
    t_settle   : time at which y last exits the ±5% band around y_final
    undershoot : minimum value of y after the peak (post-peak nadir)
"""

import numpy as np
from scipy.integrate import solve_ivp


def run_model(params: dict) -> dict:
    k_bind   = params['k_bind']    # PFAS adsorption rate (1/time)
    k_des    = params['k_des']     # desorption / regeneration rate (1/time)
    k_inh    = params['k_inh']     # fast output→sensor inhibition
    k_adapt  = params['k_adapt']   # slow adaptation coupling (h→sensor)
    k_trans  = params['k_trans']   # sensor→microfluidic coupling gain
    k_rel    = params['k_rel']     # microfluidic relaxation rate (1/time)
    k_gain   = params['k_gain']    # electrochemical transduction gain
    k_fb     = params['k_fb']      # adaptive feedback decay rate (1/time)
    k_h_on   = params['k_h_on']    # adaptation activation rate (y→h)
    k_h_off  = params['k_h_off']   # adaptation recovery rate (1/time)
    T_end    = params['T_end']     # simulation window (normalized time)

    def system(t, state):
        s, m, y, h = state

        # Nanosensor: PFAS binding with fast + slow inhibition
        ds = k_bind * (1.0 - s) - k_des * s - k_inh * y * s - k_adapt * h * s

        # Microfluidic transport layer
        dm = k_trans * s - k_rel * m

        # Electrochemical output with adaptive feedback
        dy = k_gain * m - k_fb * y

        # Slow adaptation (receptor desensitization analog)
        dh = k_h_on * y - k_h_off * h

        return [ds, dm, dy, dh]

    sol = solve_ivp(
        system,
        [0.0, T_end],
        [0.0, 0.0, 0.0, 0.0],
        method='RK45',
        max_step=T_end / 500.0,
        dense_output=True,
        rtol=1e-6,
        atol=1e-8,
    )

    N = 2000
    t_eval = np.linspace(0.0, T_end, N)
    states = sol.sol(t_eval)
    y_out  = states[2]

    # ── Amplitude ──────────────────────────────────────────────────────────────
    y_peak  = float(np.max(y_out))
    y_final = float(np.mean(y_out[int(0.98 * N):]))   # mean of last 2%   # mean of last 2%

    idx_peak = int(np.argmax(y_out))

    # ── Decay constant (log-linear fit on post-peak excess) ────────────────────
    y_after = y_out[idx_peak:]
    t_after = t_eval[idx_peak:] - t_eval[idx_peak]
    excess  = y_after - y_final
    decay   = 0.0
    if excess[0] > 1e-6:
        # Use only the initial decay region (first 30% of excess range)
        cutoff = excess[0] * 0.30
        valid  = (excess > cutoff) & (excess > 0)
        if valid.sum() > 5:
            log_ex = np.log(np.maximum(excess[valid], 1e-30))
            t_v    = t_after[valid]
            if t_v[-1] > t_v[0] + 1e-9:
                coeffs = np.polyfit(t_v, log_ex, 1)
                decay  = float(max(-coeffs[0], 0.0))

    # ── Timing: t_peak ─────────────────────────────────────────────────────────
    t_peak_val = float(t_eval[idx_peak])

    # ── Rise time: 10% → 90% of y_peak on rising edge ─────────────────────────
    rise_seg = y_out[:idx_peak + 1]
    t_seg    = t_eval[:idx_peak + 1]
    y10 = 0.10 * y_peak
    y90 = 0.90 * y_peak

    idx_10 = int(np.searchsorted(rise_seg, y10))
    idx_90 = int(np.searchsorted(rise_seg, y90))
    idx_10 = min(idx_10, len(t_seg) - 1)
    idx_90 = min(idx_90, len(t_seg) - 1)
    rise_time = float(t_seg[idx_90] - t_seg[idx_10]) if idx_90 > idx_10 else 0.0

    # ── Settling time: last time |y - y_final| > 5% band ──────────────────────
    band    = 0.05 * abs(y_final) if abs(y_final) > 1e-9 else 0.05
    outside = np.abs(y_out - y_final) > band
    last_out = int(np.max(np.where(outside)[0])) if outside.any() else 0
    t_settle = float(t_eval[last_out])

    # ── Undershoot: minimum of y after peak ────────────────────────────────────
    undershoot = float(np.min(y_out[idx_peak:]))

    return {
        'y_peak':     y_peak,
        'y_final':    y_final,
        'decay':      decay,
        't_peak':     t_peak_val,
        'rise_time':  rise_time,
        't_settle':   t_settle,
        'undershoot': undershoot,
    }
