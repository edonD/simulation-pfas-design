"""
model.py — Closed-Loop PFAS Nanobiosensor v11: Oscillator + Adaptive Target

Architecture: 5-state bioelectronic nanomicrosystem.

States:
    x  : nanosensor input (first-order binding with output inhibition)
    y  : electrochemical output (second-order oscillator)
    z  : output rate
    b  : burst amplification (transient gain)
    h  : slow adaptation (suppresses sensor target)

Key design:
    - Second-order oscillator: ζ, ωn control timing and base damping
    - Burst b: controls peak amplitude independent of steady state
    - Adaptation h: builds up proportional to y, suppresses sensor target
      → Accelerates post-peak decay (target drops as h grows)
      → Deepens undershoot (lower target during peak-induced h accumulation)
      → Recovers at steady state (h reaches equilibrium)
    - Sensor inhibition k_inh*y*x: additional decay acceleration
"""

import numpy as np


def run_model(params: dict) -> dict:
    k_on    = params['k_on']
    k_off   = params['k_off']
    k_inh   = params['k_inh']
    wn      = params['wn']
    zeta    = params['zeta']
    K       = params['K']
    b0      = params['b0']
    k_bd    = params['k_bd']
    k_ho    = params['k_ho']       # h activation rate
    k_hd    = params['k_hd']       # h decay rate
    k_ha    = params['k_ha']       # h → target suppression strength
    T_end   = params['T_end']

    N = 2000
    dt = T_end / N
    t_eval = np.linspace(0.0, T_end, N + 1)
    y_out = np.empty(N + 1)

    x, y, z, b, h = 0.0, 0.0, 0.0, b0, 0.0
    y_out[0] = 0.0

    wn2 = wn * wn
    two_zeta_wn = 2.0 * zeta * wn

    for i in range(N):
        def deriv(x_, y_, z_, b_, h_):
            # Sensor with output-dependent inhibition
            dx = k_on * (1.0 - x_) - k_off * x_ - k_inh * y_ * x_

            # Target with burst and adaptive suppression
            h_supp = 1.0 / (1.0 + k_ha * h_)   # saturating suppression
            target = K * (1.0 + b_) * x_ * h_supp

            # Second-order output dynamics
            dz = wn2 * (target - y_) - two_zeta_wn * z_
            dy = z_

            # Burst decay
            db = -k_bd * b_

            # Slow adaptation
            dh = k_ho * y_ - k_hd * h_

            return dx, dy, dz, db, dh

        k1 = deriv(x, y, z, b, h)
        k2 = deriv(x+.5*dt*k1[0], y+.5*dt*k1[1], z+.5*dt*k1[2], b+.5*dt*k1[3], h+.5*dt*k1[4])
        k3 = deriv(x+.5*dt*k2[0], y+.5*dt*k2[1], z+.5*dt*k2[2], b+.5*dt*k2[3], h+.5*dt*k2[4])
        k4 = deriv(x+dt*k3[0], y+dt*k3[1], z+dt*k3[2], b+dt*k3[3], h+dt*k3[4])

        x += dt/6.0 * (k1[0] + 2*k2[0] + 2*k3[0] + k4[0])
        y += dt/6.0 * (k1[1] + 2*k2[1] + 2*k3[1] + k4[1])
        z += dt/6.0 * (k1[2] + 2*k2[2] + 2*k3[2] + k4[2])
        b += dt/6.0 * (k1[3] + 2*k2[3] + 2*k3[3] + k4[3])
        h += dt/6.0 * (k1[4] + 2*k2[4] + 2*k3[4] + k4[4])

        x = max(0.0, min(x, 1.0))
        y = max(0.0, y)
        b = max(0.0, b)
        h = max(0.0, h)

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
