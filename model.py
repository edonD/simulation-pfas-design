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


def run_model(params: dict) -> dict:
    k_bind   = params['k_bind']
    k_des    = params['k_des']
    k_inh    = params['k_inh']
    k_adapt  = params['k_adapt']
    k_trans  = params['k_trans']
    k_rel    = params['k_rel']
    k_gain   = params['k_gain']
    k_fb     = params['k_fb']
    k_h_on   = params['k_h_on']
    k_h_off  = params['k_h_off']
    T_end    = params['T_end']

    # Fixed-step RK4 integration for speed
    N = 2000
    dt = T_end / N
    t_eval = np.linspace(0.0, T_end, N + 1)
    y_out = np.empty(N + 1)

    s, m, y, h = 0.0, 0.0, 0.0, 0.0
    y_out[0] = 0.0

    for i in range(N):
        # RK4 step
        def deriv(s_, m_, y_, h_):
            ds = k_bind * (1.0 - s_) - k_des * s_ - k_inh * y_ * s_ - k_adapt * h_ * s_
            dm = k_trans * s_ - k_rel * m_
            dy = k_gain * m_ - k_fb * y_
            dh = k_h_on * y_ - k_h_off * h_
            return ds, dm, dy, dh

        k1s, k1m, k1y, k1h = deriv(s, m, y, h)
        k2s, k2m, k2y, k2h = deriv(s + 0.5*dt*k1s, m + 0.5*dt*k1m, y + 0.5*dt*k1y, h + 0.5*dt*k1h)
        k3s, k3m, k3y, k3h = deriv(s + 0.5*dt*k2s, m + 0.5*dt*k2m, y + 0.5*dt*k2y, h + 0.5*dt*k2h)
        k4s, k4m, k4y, k4h = deriv(s + dt*k3s, m + dt*k3m, y + dt*k3y, h + dt*k3h)

        s += dt/6.0 * (k1s + 2*k2s + 2*k3s + k4s)
        m += dt/6.0 * (k1m + 2*k2m + 2*k3m + k4m)
        y += dt/6.0 * (k1y + 2*k2y + 2*k3y + k4y)
        h += dt/6.0 * (k1h + 2*k2h + 2*k3h + k4h)

        y_out[i + 1] = y

    N1 = N + 1

    # ── Amplitude ──────────────────────────────────────────────────────────────
    y_peak  = float(np.max(y_out))
    y_final = float(np.mean(y_out[int(0.98 * N1):]))   # mean of last 2%

    idx_peak = int(np.argmax(y_out))

    # ── Decay constant (log-linear fit on post-peak excess) ────────────────────
    y_after = y_out[idx_peak:]
    t_after = t_eval[idx_peak:] - t_eval[idx_peak]
    excess  = y_after - y_final
    decay   = 0.0
    if excess[0] > 1e-6:
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
