# 3D Microfluidic Chip CAD Design

You are an autonomous design agent. Your goal: produce a complete, fabrication-ready 3D CAD model of the PFAS nanobiosensor microfluidic chip from the simulation project.

**The chip was already designed and simulated** in `../simulation-pfas-design/`. The simulation proved that a 5-state system (sensor + transport delay + oscillator + burst) meets all 7 performance specs. Now you must turn that into a physical 3D model.

---

## The Tool: CadQuery

Use **CadQuery** (Python-based parametric CAD) to build the 3D model. CadQuery can:
- Create precise 3D geometry from Python code
- Export to STEP (for machining), STL (for 3D printing), and SVG (for laser cutting)
- Handle boolean operations (cut channels into substrates)
- Parameterize everything (dimensions from a config file)

---

## What To Build

The chip has **4 physical layers** that stack together:

### Layer 1: Substrate (bottom)
- Silicon or glass slab
- Dimensions: 5.0 mm x 3.5 mm x 0.5 mm
- Contains recesses for electrode routing on top surface

### Layer 2: Electrode Layer
- Three electrodes patterned on top of substrate: Working (WE), Reference (RE), Counter (CE)
- Interdigitated finger pattern for WE and CE
- Electrode area: ~1.5 mm x 2.0 mm (left zone of chip)
- Connection traces running to bond pads on the right edge
- Gold, 100 nm thick (modeled as thin extrusions for visualization)

### Layer 3: Microfluidic Channel Layer (PDMS)
- PDMS slab: 5.0 mm x 3.5 mm x 1.0 mm
- **Inlet port**: circular hole, 0.5 mm diameter, top-left
- **Outlet port**: circular hole, 0.5 mm diameter, top-right
- **Sensor chamber**: rectangular pocket over electrode area, 1.5 mm x 2.0 mm x 0.1 mm deep
- **Serpentine delay channel**: connects sensor chamber to outlet
  - Channel width: 0.2 mm
  - Channel depth: 0.1 mm
  - Serpentine with multiple U-turns in the middle zone of the chip
  - Total path length: ~20 mm (to achieve τ_d = 2.0 seconds at 10 µL/min flow rate)
  - The serpentine is the key feature — this is what creates the transport delay xd(t)

### Layer 4: Lid (top, optional)
- Thin glass or PDMS cover: 5.0 mm x 3.5 mm x 0.2 mm
- Holes aligned with inlet/outlet ports

### Bond Pads
- 4 rectangular pads on the right edge of the substrate (VDD, GND, OUT, CLK)
- Each pad: 0.4 mm x 0.3 mm

---

## Files

| File | Role | Edit? |
|------|------|-------|
| `model.py` | **Your CAD model. Build the geometry here.** | YES |
| `dimensions.json` | **All dimensions and parameters** | YES |
| `specs.json` | Target specs for the geometry | NO |
| `evaluate.py` | Evaluation harness — checks geometry meets specs | NO |
| `program.md` | These instructions | NO |

---

## The Experiment Loop

### 1. Design
Edit `model.py` to create the 3D geometry using CadQuery. The model must:
- Read all dimensions from `dimensions.json` (never hardcode)
- Export STEP file: `output/chip_assembly.step`
- Export STL files: `output/substrate.stl`, `output/channels.stl`, `output/lid.stl`
- Export top-view SVG: `output/top_view.svg`
- Return a metrics dict with geometric measurements

### 2. Evaluate
```bash
python3 evaluate.py --quick   # fast check
python3 evaluate.py           # full evaluation
```

### 3. Iterate
If specs fail, adjust `model.py` and/or `dimensions.json`, commit, and retry.

---

## Design Constraints

### Serpentine Channel Design Rules
- Minimum channel width: 0.1 mm (100 µm) — limited by soft lithography resolution
- Maximum channel width: 0.5 mm
- Minimum wall between channels: 0.1 mm
- Channel depth: 0.05 – 0.15 mm
- U-turn radius: ≥ 0.15 mm (to avoid dead zones)
- Total path length must be within ±10% of target (calculated from flow rate and delay)

### Chip Design Rules
- All features must fit within chip boundary with 0.2 mm edge margin
- Inlet/outlet ports must be accessible from top surface
- Bond pads must be on the right edge, accessible for wire bonding
- Sensor chamber must align over electrode area

### Export Requirements
- STEP file must be valid and contain all layers as separate bodies
- STL files must be watertight (manifold)
- All dimensions in millimeters

---

## Specs (what evaluate.py checks)

| Spec | Target | Tolerance | What it checks |
|------|--------|-----------|---------------|
| `chip_length` | 5.0 mm | ±5% | Overall chip X dimension |
| `chip_width` | 3.5 mm | ±5% | Overall chip Y dimension |
| `channel_path_length` | 20.0 mm | ±10% | Total serpentine channel path length |
| `channel_width` | 0.2 mm | ±20% | Channel cross-section width |
| `channel_depth` | 0.1 mm | ±20% | Channel cross-section depth |
| `sensor_chamber_area` | 3.0 mm² | ±20% | Area of sensor pocket (WxL) |
| `n_bond_pads` | 4 | exact | Number of bond pads |
| `inlet_diameter` | 0.5 mm | ±20% | Inlet port diameter |
| `outlet_diameter` | 0.5 mm | ±20% | Outlet port diameter |
| `step_file_valid` | true | exact | STEP file exports without error |
| `stl_watertight` | true | exact | STL meshes are manifold |

---

## Rules

- Edit ONLY `model.py` and `dimensions.json`
- NEVER modify `evaluate.py`, `specs.json`, or `program.md`
- NEVER hardcode dimensions — use `dimensions.json`
- ALWAYS commit before running evaluation
- NEVER stop until all specs are met
- Export files must go in `output/` directory

---

## Practical Guidance

- Start simple: get the substrate and a straight channel working first
- Then add the serpentine (hardest part — getting path length right)
- Then add electrodes and bond pads
- Then the lid and ports
- CadQuery's `Workplane.polyline()` or `spline()` can trace the serpentine path
- Use `Workplane.cutBlind()` or `cut()` for channels
- Use `Workplane.union()` to assemble layers

---

## End Condition

You are done when:
- All 11 specs pass
- STEP and STL files export successfully
- The design is physically realizable (no overlapping features, no impossible geometries)
- Commit: `git add -A && git commit -m "SOLVED | <description>"`
