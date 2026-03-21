"""
physics_model.py — Multi-physics simulation of a PFAS POC blood test strip.

Models 5 coupled stages:
  1. Sample preparation (protein denaturation → PFAS release)
  2. Capillary transport (advection-diffusion through strip)
  3. MIP binding (Langmuir kinetics at electrode surface)
  4. Electrochemical signal (TEMPO redox suppression via SWV)
  5. Signal processing (noise, LOD, calibration)

All parameters from strip_config.json. All equations from published literature.
"""
import json
import numpy as np
from scipy.optimize import curve_fit


class StripSimulation:
    def __init__(self, config_path="strip_config.json"):
        with open(config_path) as f:
            self.cfg = json.load(f)

    def run(self, c_PFOS_ng_mL, matrix="buffer", rng=None, param_noise=None):
        """Run full 5-stage simulation for one PFOS concentration.

        Args:
            c_PFOS_ng_mL: PFOS concentration in ng/mL
            matrix: "buffer", "serum_10pct", or "whole_blood"
            rng: numpy random generator for noise (None = no noise)
            param_noise: dict of parameter multipliers for Monte Carlo

        Returns: dict with time arrays and all intermediate results
        """
        cfg = self.cfg
        sim = cfg["simulation"]
        dt = sim["dt_s"]
        t_total = sim["t_total_s"]
        t = np.arange(0, t_total + dt, dt)
        N = len(t)

        mx = cfg["matrix_effects"].get(matrix, cfg["matrix_effects"]["buffer"])

        # Get MIP parameters (with optional Monte Carlo noise)
        sp = cfg["sample_preparation"]
        ct = cfg["capillary_transport"]
        mb = cfg["mip_binding"]
        ec = cfg["electrochemistry"]
        nm = cfg["noise_model"]

        ka = mb["ka_per_M_per_s"]
        kd = mb["kd_per_s"]
        Gamma_max = mb["Gamma_max_mol_per_m2"]
        A_elec = np.pi * (mb["electrode_diameter_m"] / 2) ** 2
        i_baseline = ec["i_baseline_uA"]
        max_supp = ec["max_signal_suppression_frac"]

        if param_noise:
            ka *= param_noise.get("ka", 1.0)
            Gamma_max *= param_noise.get("Gamma_max", 1.0)
            A_elec *= param_noise.get("electrode_area", 1.0)
            i_baseline *= param_noise.get("baseline_current", 1.0)
            max_supp *= param_noise.get("max_suppression", 1.0)

        # Apply matrix binding efficiency
        effective_supp = max_supp * mx["binding_efficiency"]

        # ── Stage 1: Sample Preparation ──────────────────────────────────────
        c_total_M = c_PFOS_ng_mL * 1e-9 / sp["MW_PFOS"] * 1e6  # ng/mL → mol/m³ → M (mol/L)
        # Actually: ng/mL = ug/L, and 1 ug/L / (500.13 g/mol) = 1e-6/500.13 mol/L = 2e-9 M
        c_total_M = c_PFOS_ng_mL * 1e-6 / sp["MW_PFOS"]  # mol/L

        if mx["has_protein"]:
            k_denat = sp["k_denat_base_per_s"] * sp["denaturation_enhancement"]
            Alb_0 = sp["c_albumin_uM"]  # uM
            Kd_HSA = sp["Kd_PFOS_HSA_uM"]  # uM
            Alb_t = Alb_0 * np.exp(-k_denat * t)
            f_bound_t = Alb_t / (Alb_t + Kd_HSA)
            c_free_t = c_total_M * (1.0 - f_bound_t)
        else:
            c_free_t = np.full(N, c_total_M)

        # ── Stage 2: Capillary Transport ─────────────────────────────────────
        gamma = ct["surface_tension_N_per_m"]
        r_pore = ct["pore_radius_m"]
        theta_c = np.radians(ct["contact_angle_deg"])
        eta = 0.001 * mx["viscosity_factor"]  # Pa·s
        x_elec = ct["electrode_position_m"]
        D_PFOS = ct["D_PFOS_m2_per_s"]
        D_eff = D_PFOS * ct["porosity"] / ct["tortuosity"]

        # Washburn: time for flow front to reach electrode
        t_arrival = 2 * eta * x_elec ** 2 / (gamma * r_pore * np.cos(theta_c))
        v_avg = x_elec / max(t_arrival, 1e-6)

        # Simplified transport: delay + first-order dispersion
        # After flow front arrives, PFOS diffuses from bulk pore fluid to MIP surface
        # Characteristic length = pore radius (distance from pore center to wall)
        L_diff = ct["pore_radius_m"]
        tau_diff = L_diff ** 2 / (2 * D_eff)
        # Total transport delay = flow arrival + diffusive mixing
        c_electrode_t = np.zeros(N)
        for i in range(N):
            ti = t[i]
            if ti <= t_arrival:
                c_electrode_t[i] = 0.0
            else:
                t_since = ti - t_arrival
                # First-order approach to the input concentration
                mix_factor = 1.0 - np.exp(-t_since / tau_diff)
                # Sample the free PFOS at the corresponding earlier time
                c_electrode_t[i] = c_free_t[i] * mix_factor

        # Clamp to physical limits
        c_electrode_t = np.clip(c_electrode_t, 0, c_total_M * 2)

        # ── Stage 3: MIP Binding (Langmuir kinetics) ─────────────────────────
        theta = np.zeros(N)  # fractional coverage
        for i in range(N - 1):
            c_local = c_electrode_t[i]  # mol/L
            dtheta = ka * c_local * (1.0 - theta[i]) - kd * theta[i]
            theta[i + 1] = theta[i] + dt * dtheta
            theta[i + 1] = max(0.0, min(1.0, theta[i + 1]))

        # Add nonspecific binding from matrix
        theta_ns = mx["nonspecific_binding_frac"]
        theta_effective = np.clip(theta + theta_ns, 0, 1)

        # ── Stage 4: Electrochemical Signal ──────────────────────────────────
        bg_factor = mx["background_current_factor"]

        # Peak current at each time point
        # Background current factor elevates overall baseline (matrix interferents)
        # but suppression only acts on the base TEMPO redox current, not matrix background
        i_peak_t = i_baseline * (bg_factor - effective_supp * theta_effective)

        # Final SWV measurement at t_total
        theta_final = theta_effective[-1]
        i_peak_final = i_baseline * (bg_factor - effective_supp * theta_final)

        # Generate SWV voltammogram shape at final time
        E_range = np.arange(ec["swv_E_start_V"], ec["swv_E_end_V"], ec["swv_step_V"])
        sigma_E = ec["sigma_E_V"]
        E_formal = ec["E_formal_V"]

        # Faradaic peak (Gaussian approximation of surface-confined redox)
        i_faradaic = i_peak_final * np.exp(-(E_range - E_formal) ** 2 / (2 * sigma_E ** 2))

        # Double-layer background (linear baseline)
        i_background = 0.5 * mx["background_current_factor"] * np.ones_like(E_range)

        i_swv = i_faradaic + i_background

        # ── Stage 5: Signal Processing ───────────────────────────────────────
        # Add noise if rng provided
        if rng is not None:
            noise_per_point = np.sqrt(nm["thermal_noise_uA"] ** 2 +
                                      nm["dl_charging_noise_uA"] ** 2)
            i_swv += rng.normal(0, noise_per_point, len(i_swv))
            i_peak_final += rng.normal(0, noise_per_point)

        # Signal change — blank strip sees the SAME background_current_factor
        # AND the same nonspecific binding as the sample strip.
        # Only specific MIP binding should contribute to signal_change.
        i_blank = i_baseline * (bg_factor - effective_supp * theta_ns)
        signal_change_pct = (i_blank - i_peak_final) / i_blank * 100

        return {
            "t": t,
            "c_free_t": c_free_t,
            "c_electrode_t": c_electrode_t,
            "theta_t": theta,
            "theta_effective_t": theta_effective,
            "i_peak_t": i_peak_t,
            "i_peak_final_uA": i_peak_final,
            "signal_change_pct": max(0, signal_change_pct),
            "theta_final": theta_final,
            "E_range": E_range,
            "i_swv": i_swv,
            "t_arrival_s": t_arrival,
            "v_avg_m_per_s": v_avg,
            "matrix": matrix,
            "c_PFOS_ng_mL": c_PFOS_ng_mL,
        }

    def calibration_curve(self, concentrations=None, matrix="buffer", n_reps=3):
        """Run calibration curve with replicates."""
        cfg = self.cfg
        if concentrations is None:
            concentrations = cfg["simulation"]["calibration_concentrations_ng_mL"]

        results = []
        rng = np.random.default_rng(42)

        for c in concentrations:
            signals = []
            for rep in range(n_reps):
                r = self.run(c, matrix, rng=rng)
                signals.append(r["signal_change_pct"])
            results.append({
                "concentration": c,
                "signals": signals,
                "mean": np.mean(signals),
                "std": np.std(signals),
                "theta": self.run(c, matrix)["theta_final"],
            })

        # Fit Langmuir curve to non-zero concentrations
        concs = np.array([r["concentration"] for r in results if r["concentration"] > 0])
        means = np.array([r["mean"] for r in results if r["concentration"] > 0])

        def langmuir(x, S_max, Kd_app):
            return S_max * x / (Kd_app + x)

        try:
            popt, pcov = curve_fit(langmuir, concs, means,
                                   p0=[15, 50], bounds=([0, 0.01], [100, 10000]))
            S_max, Kd_app = popt
            fit_success = True

            # R² calculation
            y_pred = langmuir(concs, *popt)
            ss_res = np.sum((means - y_pred) ** 2)
            ss_tot = np.sum((means - np.mean(means)) ** 2)
            r_squared = 1 - ss_res / max(ss_tot, 1e-30)
        except Exception:
            S_max, Kd_app = 18.4, 50
            fit_success = False
            r_squared = 0

        # LOD calculation
        blank_results = [r for r in results if r["concentration"] == 0]
        if blank_results:
            sigma_blank = blank_results[0]["std"]
        else:
            sigma_blank = results[0]["std"]

        if fit_success and Kd_app > 0:
            sensitivity = S_max / Kd_app  # slope at origin (% per ng/mL)
            LOD = 3 * max(sigma_blank, 0.01) / max(sensitivity, 1e-10)
        else:
            LOD = float('inf')

        return {
            "concentrations": [r["concentration"] for r in results],
            "means": [r["mean"] for r in results],
            "stds": [r["std"] for r in results],
            "S_max": S_max,
            "Kd_app": Kd_app,
            "LOD": LOD,
            "r_squared": r_squared,
            "fit_success": fit_success,
            "sigma_blank": sigma_blank,
            "sensitivity": S_max / Kd_app if Kd_app > 0 else 0,
            "matrix": matrix,
        }

    def monte_carlo(self, c_PFOS_ng_mL, n_strips=500, matrix="buffer"):
        """Run Monte Carlo simulation for strip-to-strip variability."""
        mc_cfg = self.cfg["monte_carlo"]
        param_cvs = mc_cfg["param_cv"]
        rng = np.random.default_rng(123)

        signals = []
        for i in range(n_strips):
            noise = {}
            for param, cv in param_cvs.items():
                noise[param] = max(0.1, 1.0 + rng.normal(0, cv))

            r = self.run(c_PFOS_ng_mL, matrix, rng=rng, param_noise=noise)
            signals.append(r["signal_change_pct"])

        signals = np.array(signals)
        return {
            "c_PFOS_ng_mL": c_PFOS_ng_mL,
            "signals": signals,
            "mean": float(np.mean(signals)),
            "std": float(np.std(signals)),
            "cv_pct": float(np.std(signals) / max(np.mean(signals), 1e-10) * 100),
            "n_strips": n_strips,
            "matrix": matrix,
        }

    def sensitivity_analysis(self, c_PFOS_ng_mL=10.0, matrix="buffer"):
        """Vary each parameter ±50% and measure impact on signal."""
        base = self.run(c_PFOS_ng_mL, matrix)
        base_signal = base["signal_change_pct"]

        params_to_vary = {
            "ka": ("mip_binding", "ka_per_M_per_s"),
            "kd": ("mip_binding", "kd_per_s"),
            "Gamma_max": ("mip_binding", "Gamma_max_mol_per_m2"),
            "k_denat": ("sample_preparation", "k_denat_base_per_s"),
            "D_PFOS": ("capillary_transport", "D_PFOS_m2_per_s"),
            "max_suppression": ("electrochemistry", "max_signal_suppression_frac"),
            "i_baseline": ("electrochemistry", "i_baseline_uA"),
            "electrode_diameter": ("mip_binding", "electrode_diameter_m"),
            "electrode_position": ("capillary_transport", "electrode_position_m"),
        }

        results = {}
        for name, (section, key) in params_to_vary.items():
            original = self.cfg[section][key]
            signals = {}
            for factor in [0.5, 0.75, 1.0, 1.25, 1.5]:
                self.cfg[section][key] = original * factor
                r = self.run(c_PFOS_ng_mL, matrix)
                signals[factor] = r["signal_change_pct"]
            self.cfg[section][key] = original  # restore

            # Elasticity: (dS/S) / (dp/p) at ±50%
            if base_signal > 0:
                elasticity = (signals[1.5] - signals[0.5]) / base_signal
            else:
                elasticity = 0
            results[name] = {
                "signals": signals,
                "elasticity": elasticity,
                "base_signal": base_signal,
            }

        return results


if __name__ == "__main__":
    sim = StripSimulation()

    # Quick test
    r = sim.run(10.0, "buffer")
    print(f"10 ng/mL PFOS in buffer:")
    print(f"  Transport arrival: {r['t_arrival_s']:.2f} s")
    print(f"  Final theta: {r['theta_final']:.4f}")
    print(f"  Signal change: {r['signal_change_pct']:.2f}%")
    print(f"  Peak current: {r['i_peak_final_uA']:.2f} uA")

    r = sim.run(10.0, "whole_blood")
    print(f"\n10 ng/mL PFOS in whole blood:")
    print(f"  Transport arrival: {r['t_arrival_s']:.2f} s")
    print(f"  Final theta: {r['theta_final']:.4f}")
    print(f"  Signal change: {r['signal_change_pct']:.2f}%")

    cal = sim.calibration_curve(matrix="buffer")
    print(f"\nCalibration (buffer):")
    print(f"  LOD: {cal['LOD']:.2f} ng/mL")
    print(f"  R²: {cal['r_squared']:.4f}")
    print(f"  S_max: {cal['S_max']:.2f}%")
    print(f"  Kd_app: {cal['Kd_app']:.1f} ng/mL")
