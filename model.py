"""
model.py — Closed-Loop PFAS Nanobiosensor v12: Oscillator + Transport Delay

Architecture: 5-state bioelectronic nanomicrosystem.

States:
    x  : nanosensor surface occupancy (first-order binding)
    xd : delayed sensor signal (first-order transport lag)
    y  : electrochemical output (second-order oscillator)
    z  : output rate
    b  : burst amplification

Key design:
    - Transport delay xd introduces time lag τ_delay, shifting t_peak later
    - Second-order oscillator with ζ, ωn for timing and oscillation
    - Burst b for peak amplification
    - 9 parameters, well-separated spec control
"""

import numpy as np


def run_model(params: dict) -> dict:
    k_on    = params['k_on']
    k_off   = params['k_off']
    tau_d   = params['tau_d']      # transport delay time constant
    wn      = params['wn']
    zeta    = params['zeta']
    K       = params['K']
    b0      = params['b0']
    k_bd    = params['k_bd']
    T_end   = params['T_end']

    N = 2000
    dt = T_end / N
    t_eval = np.linspace(0.0, T_end, N + 1)
    y_out = np.empty(N + 1)

    x, xd, y, z, b = 0.0, 0.0, 0.0, 0.0, b0
    y_out[0] = 0.0

    wn2 = wn * wn
    two_zeta_wn = 2.0 * zeta * wn
    inv_tau = 1.0 / tau_d

    for i in range(N):
        def deriv(x_, xd_, y_, z_, b_):
            # Sensor binding
            dx = k_on * (1.0 - x_) - k_off * x_

            # Transport delay (first-order lag)
            dxd = (x_ - xd_) * inv_tau

            # Target with burst using delayed sensor
            target = K * (1.0 + b_) * xd_

            # Second-order output dynamics
            dz = wn2 * (target - y_) - two_zeta_wn * z_
            dy = z_

            # Burst decay
            db = -k_bd * b_

            return dx, dxd, dy, dz, db

        k1 = deriv(x, xd, y, z, b)
        k2 = deriv(x+.5*dt*k1[0], xd+.5*dt*k1[1], y+.5*dt*k1[2], z+.5*dt*k1[3], b+.5*dt*k1[4])
        k3 = deriv(x+.5*dt*k2[0], xd+.5*dt*k2[1], y+.5*dt*k2[2], z+.5*dt*k2[3], b+.5*dt*k2[4])
        k4 = deriv(x+dt*k3[0], xd+dt*k3[1], y+dt*k3[2], z+dt*k3[3], b+dt*k3[4])

        x  += dt/6.0 * (k1[0] + 2*k2[0] + 2*k3[0] + k4[0])
        xd += dt/6.0 * (k1[1] + 2*k2[1] + 2*k3[1] + k4[1])
        y  += dt/6.0 * (k1[2] + 2*k2[2] + 2*k3[2] + k4[2])
        z  += dt/6.0 * (k1[3] + 2*k2[3] + 2*k3[3] + k4[3])
        b  += dt/6.0 * (k1[4] + 2*k2[4] + 2*k3[4] + k4[4])

        x  = max(0.0, min(x, 1.0))
        xd = max(0.0, min(xd, 1.0))
        y  = max(0.0, y)
        b  = max(0.0, b)

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
