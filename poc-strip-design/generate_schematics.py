#!/usr/bin/env python3
"""
generate_schematics.py — Generate circuit schematics for the PFAS POC strip
readout electronics using the cir2sch API, then render to PNG with xschem.
"""
import os
import subprocess
from openai import OpenAI

API_BASE = "http://18.232.161.171:8000/v1"
MODEL_ID = "cir2sch-fft-4b"

SYSTEM_MSG = (
    "You are an expert analog circuit designer. Given a SPICE netlist, "
    "generate the corresponding xschem schematic (.sch) file with proper "
    "component placement and wire routing. The schematic should follow "
    "analog design conventions: signal flows left-to-right, power top-to-bottom, "
    "differential pairs symmetric, current mirrors vertical, clean wire routing."
)

# Circuit netlists for the PFAS POC strip readout electronics
CIRCUITS = {
    "transimpedance_amplifier": {
        "description": "Transimpedance amplifier (TIA) — converts electrode current to voltage",
        "netlist": """\
* Transimpedance Amplifier for electrochemical sensor readout
* Converts picoamp-to-microamp electrode current into voltage
.subckt tia VDD VSS SENSOR_IN VOUT VREF
* Input stage - folded cascode for high gain
M1 NET1 SENSOR_IN VREF VSS sky130_fd_pr__nfet_01v8 W=10 L=0.5
M2 NET1 NET1 VDD VDD sky130_fd_pr__pfet_01v8 W=20 L=0.5
* Output buffer
M3 VOUT NET1 VDD VDD sky130_fd_pr__pfet_01v8 W=20 L=0.15
M4 VOUT VBIAS VSS VSS sky130_fd_pr__nfet_01v8 W=10 L=0.15
* Feedback resistor (1 MOhm equivalent using MOSFET)
M5 VOUT VREF SENSOR_IN VSS sky130_fd_pr__nfet_01v8 W=0.5 L=10
* Bias
M6 VBIAS VBIAS VSS VSS sky130_fd_pr__nfet_01v8 W=2 L=2
.ends tia""",
    },

    "potentiostat": {
        "description": "Potentiostat — controls electrode potential for SWV measurement",
        "netlist": """\
* Simple potentiostat for 3-electrode electrochemical cell
* WE=working electrode, RE=reference electrode, CE=counter electrode
.subckt potentiostat VDD VSS VDAC WE RE CE
* Control amplifier - forces RE to track VDAC
M1 NET1 VDAC NET3 VSS sky130_fd_pr__nfet_01v8 W=4 L=0.5
M2 NET2 RE NET3 VSS sky130_fd_pr__nfet_01v8 W=4 L=0.5
M3 NET1 NET1 VDD VDD sky130_fd_pr__pfet_01v8 W=8 L=0.5
M4 NET2 NET1 VDD VDD sky130_fd_pr__pfet_01v8 W=8 L=0.5
* Tail current source
M5 NET3 IBIAS VSS VSS sky130_fd_pr__nfet_01v8 W=4 L=1
* Output stage drives counter electrode
M6 CE NET2 VDD VDD sky130_fd_pr__pfet_01v8 W=40 L=0.15
M7 CE IBIAS VSS VSS sky130_fd_pr__nfet_01v8 W=20 L=0.15
* Bias generation
M8 IBIAS IBIAS VSS VSS sky130_fd_pr__nfet_01v8 W=2 L=2
.ends potentiostat""",
    },

    "swv_generator": {
        "description": "SWV waveform generator — produces the staircase + pulse waveform",
        "netlist": """\
* Square Wave Voltammetry waveform generator
* Generates staircase with superimposed square pulses
.subckt swv_gen VDD VSS CLK STEP VOUT
* DAC current source (R-2R ladder simplified)
M1 NET1 STEP VSS VSS sky130_fd_pr__nfet_01v8 W=2 L=0.5
M2 NET1 NET1 VDD VDD sky130_fd_pr__pfet_01v8 W=4 L=0.5
* Square pulse superposition
M3 NET2 CLK NET1 VSS sky130_fd_pr__nfet_01v8 W=4 L=0.15
M4 NET2 CLK VDD VDD sky130_fd_pr__pfet_01v8 W=8 L=0.15
* Output buffer
M5 VOUT NET2 VDD VDD sky130_fd_pr__pfet_01v8 W=10 L=0.15
M6 VOUT VBIAS VSS VSS sky130_fd_pr__nfet_01v8 W=5 L=0.15
M7 VBIAS VBIAS VSS VSS sky130_fd_pr__nfet_01v8 W=2 L=2
.ends swv_gen""",
    },

    "current_mirror": {
        "description": "Cascode current mirror — provides stable bias currents for all blocks",
        "netlist": """\
* Cascode NMOS current mirror for bias generation
.subckt bias_mirror VDD IREF IOUT1 IOUT2 GND
M1 IREF IREF GND GND sky130_fd_pr__nfet_01v8 W=2 L=1
M2 NET1 IREF GND GND sky130_fd_pr__nfet_01v8 W=2 L=1
M3 NET2 IREF GND GND sky130_fd_pr__nfet_01v8 W=4 L=1
M4 IOUT1 VCAS NET1 GND sky130_fd_pr__nfet_01v8 W=2 L=0.5
M5 IOUT2 VCAS NET2 GND sky130_fd_pr__nfet_01v8 W=4 L=0.5
M6 VCAS VCAS IREF GND sky130_fd_pr__nfet_01v8 W=2 L=0.5
.ends bias_mirror""",
    },
}


def get_client():
    return OpenAI(api_key="none", base_url=API_BASE)


def generate_schematic(client, netlist):
    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {"role": "system", "content": SYSTEM_MSG},
            {"role": "user", "content": f"Convert this SPICE netlist to an xschem schematic:\n\n{netlist}"},
        ],
        max_tokens=4096,
        temperature=0.1,
    )
    return response.choices[0].message.content or ""


def render_to_png(sch_path, png_path):
    """Use xschem in batch mode with Xvfb to render .sch to .png"""
    # xschem can export to SVG/PDF/PNG in batch mode
    cmd = [
        "xvfb-run", "-a",
        "xschem", "--tcl",
        f'xschem load {sch_path}; xschem export png {png_path}; exit',
        "--no_x", "-q"
    ]
    # Alternative: use xschem's command-line export
    # Try the simpler batch approach first
    try:
        result = subprocess.run(
            ["xvfb-run", "-a", "xschem", "-n", "-s", "-q", "--tcl",
             f"set fname {sch_path}; source $fname; xschem save_as_png {png_path}; exit"],
            capture_output=True, text=True, timeout=30
        )
        if os.path.exists(png_path):
            return True
    except Exception:
        pass

    # Fallback: use xschem's --png flag
    try:
        result = subprocess.run(
            ["xvfb-run", "-a", "xschem", "-n", "-q", "--png", png_path, sch_path],
            capture_output=True, text=True, timeout=30
        )
        if os.path.exists(png_path):
            return True
    except Exception:
        pass

    # Another fallback: use the batch script approach
    tcl_script = f"""
xschem load {os.path.abspath(sch_path)}
xschem png {os.path.abspath(png_path)}
exit
"""
    tcl_path = sch_path + ".tcl"
    with open(tcl_path, "w") as f:
        f.write(tcl_script)

    try:
        result = subprocess.run(
            ["xvfb-run", "-a", "xschem", "--script", tcl_path, "-n", "-q"],
            capture_output=True, text=True, timeout=30
        )
        os.remove(tcl_path)
        if os.path.exists(png_path):
            return True
    except Exception:
        pass

    return False


def validate(schematic):
    lines = schematic.strip().split("\n")
    return {
        "has_header": any("xschem" in l.lower() or "v {" in l for l in lines[:5]),
        "num_components": sum(1 for l in lines if l.strip().startswith("C {")),
        "num_wires": sum(1 for l in lines if l.strip().startswith("N ")),
        "total_lines": len(lines),
    }


def main():
    os.makedirs("schematics", exist_ok=True)
    client = get_client()

    print(f"Connecting to API: {API_BASE}")
    print(f"Model: {MODEL_ID}")
    print()

    results = {}
    for name, info in CIRCUITS.items():
        print(f"{'='*60}")
        print(f"  {name}: {info['description']}")
        print(f"{'='*60}")

        print("  Generating schematic from netlist...")
        try:
            sch_content = generate_schematic(client, info["netlist"])
        except Exception as e:
            print(f"  API ERROR: {e}")
            results[name] = {"status": "API_ERROR", "error": str(e)}
            continue

        v = validate(sch_content)
        print(f"  Components: {v['num_components']}, Wires: {v['num_wires']}, Lines: {v['total_lines']}")

        # Save .sch file
        sch_path = f"schematics/{name}.sch"
        with open(sch_path, "w") as f:
            f.write(sch_content)
        print(f"  Saved: {sch_path}")

        # Render to PNG
        png_path = f"schematics/{name}.png"
        rendered = render_to_png(sch_path, png_path)
        if rendered:
            print(f"  Rendered: {png_path}")
        else:
            print(f"  PNG render failed (xschem batch mode issue)")

        results[name] = {
            "status": "OK" if v["num_components"] > 0 else "EMPTY",
            "validation": v,
            "sch_path": sch_path,
            "png_path": png_path if rendered else None,
        }

        # Print first 20 lines of schematic
        print(f"\n  --- First 20 lines ---")
        for line in sch_content.split("\n")[:20]:
            print(f"  {line}")
        print(f"  ...\n")

    print(f"\n{'='*60}")
    print("  SUMMARY")
    print(f"{'='*60}")
    for name, r in results.items():
        status = r.get("status", "UNKNOWN")
        v = r.get("validation", {})
        png = "YES" if r.get("png_path") else "NO"
        print(f"  {name:30s}  {status:10s}  C={v.get('num_components',0)}  W={v.get('num_wires',0)}  PNG={png}")


if __name__ == "__main__":
    main()
