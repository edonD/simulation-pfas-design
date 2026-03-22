#!/usr/bin/env python3
"""
render_sch.py — Render xschem .sch files to PNG using xschem's native
renderer with sky130 PDK symbols.

Requires:
  - xschem (V3.4+)
  - xvfb-run (virtual framebuffer for headless rendering)
  - sky130 xschem symbols in /tmp/xschem_sky130
  - Local xschemrc configuring library paths
"""
import os
import subprocess
import shutil


def render_xschem_native(sch_path, png_path):
    """Render .sch to PNG using xschem's native batch-mode renderer.

    Uses xvfb-run for headless X11 and xschem's built-in print command
    with proper sky130 PDK symbols.
    """
    sch_abs = os.path.abspath(sch_path)
    png_abs = os.path.abspath(png_path)

    cmd = [
        "xvfb-run", "-a", "-s", "-screen 0 2560x1440x24",
        "xschem", "-n", "-q",
        sch_abs,
        "--command",
        f"xschem zoom_full; xschem print png {png_abs}; exit",
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30,
            cwd=os.path.dirname(sch_abs) or ".",
        )
        return os.path.exists(png_abs) and os.path.getsize(png_abs) > 0
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"  xschem error: {e}")
        return False


def ensure_sky130_symbols():
    """Clone sky130 xschem symbols if not already present."""
    sky130_dir = "/tmp/xschem_sky130"
    if os.path.isdir(sky130_dir) and os.path.exists(
        os.path.join(sky130_dir, "sky130_fd_pr", "nfet_01v8.sym")
    ):
        return True

    print("Downloading sky130 xschem symbols...")
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1",
             "https://github.com/StefanSchippers/xschem_sky130.git",
             sky130_dir],
            capture_output=True, timeout=60,
        )
        return os.path.exists(
            os.path.join(sky130_dir, "sky130_fd_pr", "nfet_01v8.sym")
        )
    except Exception as e:
        print(f"  Failed to download sky130 symbols: {e}")
        return False


def ensure_xschemrc():
    """Create local xschemrc if not present, configuring sky130 + devices."""
    rc_path = "xschemrc"
    if os.path.exists(rc_path):
        return

    with open(rc_path, "w") as f:
        f.write("""\
# Sky130 PDK xschem symbols
append XSCHEM_LIBRARY_PATH :/tmp/xschem_sky130
# Built-in xschem devices (lab_pin, iopin, etc.)
append XSCHEM_LIBRARY_PATH :/usr/local/share/xschem/xschem_library
# Light color scheme for clean PNG export
set dark_colorscheme 0
""")


def main():
    circuits = {
        "current_mirror":
            "Cascode Current Mirror — Stable bias currents for all blocks",
        "transimpedance_amplifier":
            "Transimpedance Amplifier (TIA) — Converts electrode current to voltage",
        "potentiostat":
            "Potentiostat Circuit — Controls electrode potential for SWV",
        "swv_generator":
            "SWV Waveform Generator — Staircase + square pulse for voltammetry",
    }

    # Pre-flight checks
    if not shutil.which("xschem"):
        print("ERROR: xschem not found in PATH")
        return
    if not shutil.which("xvfb-run"):
        print("ERROR: xvfb-run not found (install xvfb)")
        return

    ensure_sky130_symbols()
    ensure_xschemrc()

    print(f"Rendering {len(circuits)} schematics via xschem native renderer\n")

    for name, desc in circuits.items():
        sch_path = f"schematics/{name}.sch"
        png_path = f"schematics/{name}.png"

        if not os.path.exists(sch_path):
            print(f"  SKIP: {sch_path} not found")
            continue

        print(f"  {name}...")
        ok = render_xschem_native(sch_path, png_path)
        if ok:
            sz = os.path.getsize(png_path)
            print(f"    -> {png_path} ({sz:,} bytes)")
        else:
            print(f"    FAILED")

    print("\nDone.")


if __name__ == "__main__":
    main()
