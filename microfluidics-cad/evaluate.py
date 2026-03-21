"""
evaluate.py — Evaluator for microfluidic chip CAD model. DO NOT MODIFY.

Usage:
    python3 evaluate.py            # full evaluation
    python3 evaluate.py --quick    # quick check (skip STL validation)
"""
import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

SPECS_FILE = Path("specs.json")
RESULTS_FILE = Path("results.tsv")


def _load_model():
    spec = importlib.util.spec_from_file_location("model", "model.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.build_chip


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="Skip STL validation")
    args = parser.parse_args()

    specs = json.loads(SPECS_FILE.read_text())
    build_fn = _load_model()

    print(f"\n{'='*60}")
    print(f"  microfluidics CAD evaluator")
    print(f"{'='*60}\n")

    # Build the model
    try:
        metrics = build_fn()
        print("  Model built successfully.\n")
    except Exception as e:
        print(f"  BUILD FAILED: {e}\n")
        metrics = {}

    # Check STEP file
    step_path = Path("output/chip_assembly.step")
    if step_path.exists() and step_path.stat().st_size > 100:
        metrics["step_file_valid"] = True
        print(f"  STEP file: {step_path} ({step_path.stat().st_size} bytes)")
    else:
        metrics["step_file_valid"] = False
        print(f"  STEP file: MISSING or empty")

    # Check STL files
    stl_files = ["output/substrate.stl", "output/channels.stl", "output/lid.stl"]
    all_watertight = True
    for stl in stl_files:
        p = Path(stl)
        if p.exists() and p.stat().st_size > 100:
            print(f"  STL file: {p} ({p.stat().st_size} bytes)")
            if not args.quick:
                try:
                    import trimesh
                    mesh = trimesh.load(str(p))
                    if not mesh.is_watertight:
                        print(f"    WARNING: {p} is NOT watertight")
                        all_watertight = False
                    else:
                        print(f"    OK: watertight")
                except ImportError:
                    print(f"    (trimesh not installed, skipping watertight check)")
                except Exception as e:
                    print(f"    WARNING: could not validate: {e}")
                    all_watertight = False
        else:
            print(f"  STL file: {p} MISSING or empty")
            all_watertight = False

    if args.quick:
        metrics["stl_watertight"] = metrics.get("stl_watertight", True)
    else:
        metrics["stl_watertight"] = all_watertight

    # Check SVG
    svg_path = Path("output/top_view.svg")
    if svg_path.exists():
        print(f"  SVG file: {svg_path} ({svg_path.stat().st_size} bytes)")
    else:
        print(f"  SVG file: MISSING")

    # Evaluate specs
    print(f"\n{'-'*60}")
    print("  METRICS vs SPECS\n")

    tolerances = {
        "chip_length": 0.05,
        "chip_width": 0.05,
        "channel_path_length": 0.10,
        "channel_width": 0.20,
        "channel_depth": 0.20,
        "sensor_chamber_area": 0.20,
        "n_bond_pads": 0.0,
        "inlet_diameter": 0.20,
        "outlet_diameter": 0.20,
        "step_file_valid": 0.0,
        "stl_watertight": 0.0,
    }

    n_met = 0
    for key, target in specs.items():
        v = metrics.get(key, None)
        tol = tolerances.get(key, 0.05)

        if v is None:
            ok = "XX"
            err_str = "MISSING"
        elif isinstance(target, bool):
            ok = "OK" if v == target else "XX"
            err_str = f"got={v}"
        elif tol == 0.0:
            ok = "OK" if v == target else "XX"
            err_str = f"got={v}  target={target}"
        else:
            err = abs(v - target) / max(abs(target), 1e-30)
            ok = "OK" if err <= tol else "XX"
            err_str = f"got={v:.4g}  target={target}  err={err*100:.1f}%"

        if ok == "OK":
            n_met += 1
        print(f"    {ok} {key:25s}  {err_str}")

    score = n_met / len(specs)
    print(f"\n  Score: {n_met}/{len(specs)} ({score*100:.0f}%)")
    print(f"{'='*60}\n")

    # Log result
    try:
        import subprocess
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        commit = "unknown"

    with open(RESULTS_FILE, "a") as f:
        f.write(f"{commit}\t{score:.3f}\t{json.dumps(metrics)}\n")


if __name__ == "__main__":
    main()
