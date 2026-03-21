"""
model.py — Closed-Loop PFAS Nanobiosensor v8: Dual Sensor + Burst

Architecture: 6-state bioelectronic nanomicrosystem for PFAS detection.

States:
    s1 : primary nanosensor (fast, inhibited by y and h)
    s2 : secondary nanosensor (slow, uninhibited — provides steady-state baseline)
    m  : microfluidic transport / buffered signal
    y  : electrochemical output
    h  : slow adaptation (sensor suppression on s1)
    b  : burst amplification (transient gain)

Key design:
    - s1: fast binding, strongly inhibited → creates transient peak and overshoot
    - s2: slow binding, NO inhibition → rises slowly to s2_ss, contributes to y_final
    - Burst b: amplifies early signal for y_peak control
    - s2 barely contributes during peak (still rising) but fully at steady state
    - This raises y_final relative to undershoot, fixing the ratio
"""

import numpy as np


def run_model(params: dict) -> dict:
    # Primary sensor (fixed good values)
    k_bind1 = 0.5
    k_des1  = 0.034
    k_inh   = 4.84
    k_adapt = params['k_adapt']

    # Secondary sensor (slow, uninhibited)
    k_bind2 = params['k_bind2']
    k_mix   = params['k_mix']       # s2 contribution weight

    # Transport and output
    k_trans = params['k_trans']
    k_rel   = params['k_rel']
    k_gain  = params['k_gain']
    k_fb    = params['k_fb']

    # Adaptation
    k_ho    = params['k_ho']
    k_hd    = params['k_hd']

    # Burst
    b0      = params['b0']
    k_bd    = params['k_bd']

    T_end   = params['T_end']

    N = 2000
    dt = T_end / N
    t_eval = np.linspace(0.0, T_end, N + 1)
    y_out = np.empty(N + 1)

    s1, s2, m, y, h, b = 0.0, 0.0, 0.0, 0.0, 0.0, b0
    y_out[0] = 0.0

    for i in range(N):
        def deriv(s1_, s2_, m_, y_, h_, b_):
            # Primary sensor: fast binding with inhibition
            ds1 = k_bind1 * (1.0 - s1_) - k_des1 * s1_ - k_inh * y_ * s1_ - k_adapt * h_ * s1_

            # Secondary sensor: slow binding, no inhibition
            ds2 = k_bind2 * (1.0 - s2_)

            # Transport: both sensors contribute
            dm = k_trans * (s1_ + k_mix * s2_) - k_rel * m_

            # Output with burst amplification
            dy = k_gain * m_ * (1.0 + b_) - k_fb * y_

            # Slow adaptation
            dh = k_ho * y_ - k_hd * h_

            # Burst decay
            db = -k_bd * b_

            return ds1, ds2, dm, dy, dh, db

        k1 = deriv(s1, s2, m, y, h, b)
        k2 = deriv(s1+.5*dt*k1[0], s2+.5*dt*k1[1], m+.5*dt*k1[2], y+.5*dt*k1[3], h+.5*dt*k1[4], b+.5*dt*k1[5])
        k3 = deriv(s1+.5*dt*k2[0], s2+.5*dt*k2[1], m+.5*dt*k2[2], y+.5*dt*k2[3], h+.5*dt*k2[4], b+.5*dt*k2[5])
        k4 = deriv(s1+dt*k3[0], s2+dt*k3[1], m+dt*k3[2], y+dt*k3[3], h+dt*k3[4], b+dt*k3[5])

        s1 += dt/6.0 * (k1[0] + 2*k2[0] + 2*k3[0] + k4[0])
        s2 += dt/6.0 * (k1[1] + 2*k2[1] + 2*k3[1] + k4[1])
        m  += dt/6.0 * (k1[2] + 2*k2[2] + 2*k3[2] + k4[2])
        y  += dt/6.0 * (k1[3] + 2*k2[3] + 2*k3[3] + k4[3])
        h  += dt/6.0 * (k1[4] + 2*k2[4] + 2*k3[4] + k4[4])
        b  += dt/6.0 * (k1[5] + 2*k2[5] + 2*k3[5] + k4[5])

        s1 = max(0.0, min(s1, 1.0))
        s2 = max(0.0, min(s2, 1.0))
        m  = max(0.0, min(m, 1e4))
        y  = max(0.0, min(y, 1e4))
        h  = max(0.0, min(h, 1e4))
        b  = max(0.0, min(b, 1e4))

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
