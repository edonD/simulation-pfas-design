"""
model.py — Closed-Loop PFAS Nanobiosensor v7: Threshold Adaptation

Architecture: 5-state bioelectronic nanomicrosystem for PFAS detection.

States:
    s  : nanosensor surface occupancy (0–1)
    m  : microfluidic transport / buffered signal
    y  : electrochemical output (measured signal)
    h  : slow adaptation (sensor suppression, controls timing)
    g  : threshold adaptation (output inhibition, active only during peak)

Key design:
    - h handles timing: slow sensor suppression (same as original 5/7 model)
    - g is THRESHOLD-ACTIVATED: dg = k_go * max(y-y_ref, 0)² - k_gd * g
    - At steady state (y_ss < y_ref): g_ss = 0, no effect on y_final
    - During peak (y >> y_ref): g accumulates, creates undershoot via k_gi*g
    - This cleanly decouples undershoot depth from steady-state level
"""

import numpy as np


def run_model(params: dict) -> dict:
    # Fixed sensor params (from 5/7 solution)
    k_bind  = 0.5
    k_des   = 0.034
    k_inh   = 4.84

    # Free params for timing/gain
    k_adapt = params['k_adapt']
    k_trans = params['k_trans']
    k_rel   = params['k_rel']
    k_gain  = params['k_gain']
    k_fb    = params['k_fb']
    k_ho    = params['k_ho']
    k_hd    = params['k_hd']

    # Threshold adaptation for undershoot
    k_gi    = params['k_gi']      # g→output inhibition strength
    k_go    = params['k_go']      # g activation rate
    k_gd    = params['k_gd']      # g decay rate
    y_ref   = params['y_ref']     # activation threshold

    T_end   = params['T_end']

    N = 2000
    dt = T_end / N
    t_eval = np.linspace(0.0, T_end, N + 1)
    y_out = np.empty(N + 1)

    s, m, y, h, g = 0.0, 0.0, 0.0, 0.0, 0.0
    y_out[0] = 0.0

    for i in range(N):
        def deriv(s_, m_, y_, h_, g_):
            ds = k_bind * (1.0 - s_) - k_des * s_ - k_inh * y_ * s_ - k_adapt * h_ * s_
            dm = k_trans * s_ - k_rel * m_
            dy = k_gain * m_ - k_fb * y_ - k_gi * g_
            dh = k_ho * y_ - k_hd * h_

            # Threshold-activated adaptation: only active during peak
            excess = max(y_ - y_ref, 0.0)
            dg = k_go * excess * excess - k_gd * g_

            return ds, dm, dy, dh, dg

        k1 = deriv(s, m, y, h, g)
        k2 = deriv(s+0.5*dt*k1[0], m+0.5*dt*k1[1], y+0.5*dt*k1[2], h+0.5*dt*k1[3], g+0.5*dt*k1[4])
        k3 = deriv(s+0.5*dt*k2[0], m+0.5*dt*k2[1], y+0.5*dt*k2[2], h+0.5*dt*k2[3], g+0.5*dt*k2[4])
        k4 = deriv(s+dt*k3[0], m+dt*k3[1], y+dt*k3[2], h+dt*k3[3], g+dt*k3[4])

        s += dt/6.0 * (k1[0] + 2*k2[0] + 2*k3[0] + k4[0])
        m += dt/6.0 * (k1[1] + 2*k2[1] + 2*k3[1] + k4[1])
        y += dt/6.0 * (k1[2] + 2*k2[2] + 2*k3[2] + k4[2])
        h += dt/6.0 * (k1[3] + 2*k2[3] + 2*k3[3] + k4[3])
        g += dt/6.0 * (k1[4] + 2*k2[4] + 2*k3[4] + k4[4])

        s = max(0.0, min(s, 1.0))
        m = max(0.0, min(m, 1e4))
        y = max(0.0, min(y, 1e4))
        h = max(0.0, min(h, 1e4))
        g = max(0.0, min(g, 1e4))

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
