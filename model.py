"""
model.py — Closed-Loop PFAS Nanobiosensor v4: Dual-Path Adaptation + Burst

Architecture: 5-state bioelectronic nanomicrosystem for PFAS detection.

States:
    s  : nanosensor surface occupancy (0–1)
    m  : microfluidic transport / buffered signal
    y  : electrochemical output (measured signal)
    h  : slow adaptation (acts on BOTH sensor AND output for strong undershoot)
    b  : burst amplification (transient gain, exponential decay)

Key design: Adaptation h acts through two pathways:
    1. Suppresses sensor surface s (reduces gain chain input)
    2. Directly inhibits output y (subtracts from output)
    Combined effect creates deep undershoot with controllable recovery.
    Burst b provides transient peak amplification independent of steady state.
"""

import numpy as np


def run_model(params: dict) -> dict:
    k_bind   = params['k_bind']
    k_des    = params['k_des']
    k_adapt  = params['k_adapt']   # h → sensor suppression
    k_trans  = params['k_trans']
    k_rel    = params['k_rel']
    k_gain   = params['k_gain']
    k_fb     = params['k_fb']
    k_h_on   = params['k_h_on']
    k_h_off  = params['k_h_off']
    k_h_inh  = params['k_h_inh']   # h → output inhibition
    b0       = params['b0']
    k_b_dec  = params['k_b_dec']
    T_end    = params['T_end']

    N = 2000
    dt = T_end / N
    t_eval = np.linspace(0.0, T_end, N + 1)
    y_out = np.empty(N + 1)

    s, m, y, h, b = 0.0, 0.0, 0.0, 0.0, b0
    y_out[0] = 0.0

    for i in range(N):
        def deriv(s_, m_, y_, h_, b_):
            # Sensor: binding with adaptation suppression
            ds = k_bind * (1.0 - s_) - k_des * s_ - k_adapt * h_ * s_

            # Transport layer
            dm = k_trans * s_ - k_rel * m_

            # Output: burst-enhanced gain, feedback decay, adaptation inhibition
            dy = k_gain * m_ * (1.0 + b_) - k_fb * y_ - k_h_inh * h_

            # Slow adaptation (linear in y for smoother dynamics)
            dh = k_h_on * y_ - k_h_off * h_

            # Burst decay
            db = -k_b_dec * b_

            return ds, dm, dy, dh, db

        k1 = deriv(s, m, y, h, b)
        k2 = deriv(s+0.5*dt*k1[0], m+0.5*dt*k1[1], y+0.5*dt*k1[2], h+0.5*dt*k1[3], b+0.5*dt*k1[4])
        k3 = deriv(s+0.5*dt*k2[0], m+0.5*dt*k2[1], y+0.5*dt*k2[2], h+0.5*dt*k2[3], b+0.5*dt*k2[4])
        k4 = deriv(s+dt*k3[0], m+dt*k3[1], y+dt*k3[2], h+dt*k3[3], b+dt*k3[4])

        s += dt/6.0 * (k1[0] + 2*k2[0] + 2*k3[0] + k4[0])
        m += dt/6.0 * (k1[1] + 2*k2[1] + 2*k3[1] + k4[1])
        y += dt/6.0 * (k1[2] + 2*k2[2] + 2*k3[2] + k4[2])
        h += dt/6.0 * (k1[3] + 2*k2[3] + 2*k3[3] + k4[3])
        b += dt/6.0 * (k1[4] + 2*k2[4] + 2*k3[4] + k4[4])

        s = max(0.0, min(s, 1.0))
        m = max(0.0, min(m, 1e4))
        y = max(0.0, min(y, 1e4))
        h = max(0.0, min(h, 1e4))
        b = max(0.0, min(b, 1e4))

        y_out[i + 1] = y

    N1 = N + 1

    # ── Amplitude ──────────────────────────────────────────────────────────────
    y_peak  = float(np.max(y_out))
    y_final = float(np.mean(y_out[int(0.98 * N1):]))

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
