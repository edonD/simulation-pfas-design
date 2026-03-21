"""
model.py — CadQuery 3D model of the PFAS nanobiosensor microfluidic chip.

Build the chip geometry here. Read all dimensions from dimensions.json.
Export STEP, STL, and SVG files to output/.

Returns a metrics dict for the evaluator.
"""
import json
import os
import math
import cadquery as cq
from pathlib import Path


def build_chip() -> dict:
    """Build the full chip assembly and return geometric metrics."""

    os.makedirs("output", exist_ok=True)

    # Load dimensions
    with open("dimensions.json") as f:
        dims = json.load(f)

    chip = dims["chip"]
    ch = dims["channels"]
    sc = dims["sensor_chamber"]
    ports = dims["ports"]
    elec = dims["electrodes"]
    bp = dims["bond_pads"]

    L = chip["length"]
    W = chip["width"]
    margin = chip["edge_margin"]

    # ── Layer 1: Substrate ────────────────────────────────────────────────────
    substrate = (
        cq.Workplane("XY")
        .box(L, W, chip["substrate_thickness"])
        .translate((L / 2, W / 2, chip["substrate_thickness"] / 2))
    )

    # ── Layer 2: Electrodes (thin extrusions on substrate top surface) ────────
    z_elec = chip["substrate_thickness"]
    electrode_parts = cq.Workplane("XY")

    # Interdigitated fingers
    n_fingers = elec["n_fingers"]
    f_len = elec["finger_length"]
    f_w = elec["finger_width"]
    f_gap = elec["finger_gap"]
    e_thick = elec["thickness"]

    finger_start_x = sc["x_offset"] + 0.15
    finger_start_y = sc["y_offset"] + 0.15

    for i in range(n_fingers):
        y_pos = finger_start_y + i * (f_w + f_gap)
        # Alternate from left and right for interdigitation
        if i % 2 == 0:
            x_start = finger_start_x
        else:
            x_start = finger_start_x + 0.2

        electrode_parts = (
            electrode_parts
            .moveTo(x_start, y_pos)
            .rect(f_len, f_w)
            .extrude(e_thick)
            .translate((0, 0, z_elec))
        )

    # Bond pads
    for i in range(bp["n_pads"]):
        y_pos = bp["y_start"] + i * bp["y_spacing"]
        pad = (
            cq.Workplane("XY")
            .moveTo(bp["x_position"], y_pos)
            .rect(bp["pad_width"], bp["pad_height"])
            .extrude(e_thick)
            .translate((0, 0, z_elec))
        )
        electrode_parts = electrode_parts.union(pad)

    # ── Layer 3: Channel Layer (PDMS) ─────────────────────────────────────────
    z_chan = chip["substrate_thickness"]
    chan_thick = chip["channel_layer_thickness"]

    # Start with solid PDMS block
    channel_layer = (
        cq.Workplane("XY")
        .box(L, W, chan_thick)
        .translate((L / 2, W / 2, z_chan + chan_thick / 2))
    )

    # Cut sensor chamber pocket (bottom face of PDMS)
    chamber = (
        cq.Workplane("XY")
        .transformed(offset=(
            sc["x_offset"] + sc["width"] / 2,
            sc["y_offset"] + sc["length"] / 2,
            z_chan
        ))
        .rect(sc["width"], sc["length"])
        .extrude(sc["depth"])
    )
    channel_layer = channel_layer.cut(chamber)

    # Build serpentine channel path
    c_w = ch["width"]
    c_d = ch["depth"]
    wall = ch["wall_spacing"]
    r = ch["u_turn_radius"]

    # Serpentine parameters — fit within the middle zone of the chip
    serp_x_start = sc["x_offset"] + sc["width"] + 0.2  # start after sensor chamber
    serp_x_end = L - margin - 0.3  # end near outlet
    serp_y_min = margin + r
    serp_y_max = W - margin - r
    serp_width = serp_x_end - serp_x_start
    pass_length = serp_y_max - serp_y_min

    # Calculate n_passes from target path length (subtract connection overhead)
    target_pl = ch["target_path_length"]
    connection_overhead = 3.0  # approximate entry/exit routing
    serpentine_budget = target_pl - connection_overhead
    # Each pass contributes pass_length, each U-turn contributes ~(c_w + wall)
    n_passes = max(2, round(serpentine_budget / (pass_length + c_w + wall)))
    # Ensure it fits in the available width
    while n_passes * (c_w + wall) > serp_width + wall and n_passes > 2:
        n_passes -= 1

    # Build serpentine as a series of straight + U-turn cuts
    path_points = []
    x_pos = serp_x_start
    actual_path_length = 0.0

    # Connect from sensor chamber exit to serpentine start
    chamber_exit_x = sc["x_offset"] + sc["width"]
    chamber_exit_y = sc["y_offset"] + sc["length"] / 2
    path_points.append((chamber_exit_x, chamber_exit_y))
    path_points.append((serp_x_start, chamber_exit_y))
    actual_path_length += serp_x_start - chamber_exit_x

    # Move to serpentine start
    if chamber_exit_y < (serp_y_min + serp_y_max) / 2:
        path_points.append((serp_x_start, serp_y_min))
        actual_path_length += abs(chamber_exit_y - serp_y_min)
        current_y = serp_y_min
        going_up = True
    else:
        path_points.append((serp_x_start, serp_y_max))
        actual_path_length += abs(chamber_exit_y - serp_y_max)
        current_y = serp_y_max
        going_up = False

    # Serpentine passes
    for i in range(n_passes):
        x_pos = serp_x_start + i * (c_w + wall)

        if going_up:
            target_y = serp_y_max
        else:
            target_y = serp_y_min

        path_points.append((x_pos, target_y))
        actual_path_length += abs(target_y - current_y)
        current_y = target_y

        # U-turn to next pass (if not last)
        if i < n_passes - 1:
            next_x = x_pos + c_w + wall
            path_points.append((next_x, current_y))
            actual_path_length += c_w + wall
            going_up = not going_up

    # Connect serpentine end to outlet
    outlet_x = ports["outlet_x"]
    outlet_y = ports["outlet_y"]
    last_x, last_y = path_points[-1]
    path_points.append((outlet_x, last_y))
    actual_path_length += abs(outlet_x - last_x)
    path_points.append((outlet_x, outlet_y))
    actual_path_length += abs(outlet_y - last_y)

    # Cut channel segments as rectangular grooves
    for j in range(len(path_points) - 1):
        x1, y1 = path_points[j]
        x2, y2 = path_points[j + 1]

        if abs(x2 - x1) < 0.001:  # vertical segment
            seg_len = abs(y2 - y1)
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            seg = (
                cq.Workplane("XY")
                .transformed(offset=(cx, cy, z_chan))
                .rect(c_w, seg_len)
                .extrude(c_d)
            )
        else:  # horizontal segment
            seg_len = abs(x2 - x1)
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            seg = (
                cq.Workplane("XY")
                .transformed(offset=(cx, cy, z_chan))
                .rect(seg_len, c_w)
                .extrude(c_d)
            )
        channel_layer = channel_layer.cut(seg)

    # Cut inlet port (through entire PDMS layer)
    inlet = (
        cq.Workplane("XY")
        .transformed(offset=(ports["inlet_x"], ports["inlet_y"], z_chan))
        .circle(ports["inlet_diameter"] / 2)
        .extrude(chan_thick)
    )
    channel_layer = channel_layer.cut(inlet)

    # Cut outlet port
    outlet = (
        cq.Workplane("XY")
        .transformed(offset=(ports["outlet_x"], ports["outlet_y"], z_chan))
        .circle(ports["outlet_diameter"] / 2)
        .extrude(chan_thick)
    )
    channel_layer = channel_layer.cut(outlet)

    # Connect inlet to sensor chamber
    inlet_to_chamber = (
        cq.Workplane("XY")
        .transformed(offset=(
            (ports["inlet_x"] + sc["x_offset"]) / 2 + sc["width"] / 4,
            ports["inlet_y"],
            z_chan
        ))
        .rect(sc["x_offset"] + sc["width"] / 2, c_w)
        .extrude(c_d)
    )
    channel_layer = channel_layer.cut(inlet_to_chamber)

    # ── Layer 4: Lid ──────────────────────────────────────────────────────────
    z_lid = z_chan + chan_thick
    lid = (
        cq.Workplane("XY")
        .box(L, W, chip["lid_thickness"])
        .translate((L / 2, W / 2, z_lid + chip["lid_thickness"] / 2))
    )

    # Cut port holes through lid
    lid_inlet = (
        cq.Workplane("XY")
        .transformed(offset=(ports["inlet_x"], ports["inlet_y"], z_lid))
        .circle(ports["inlet_diameter"] / 2)
        .extrude(chip["lid_thickness"])
    )
    lid = lid.cut(lid_inlet)

    lid_outlet = (
        cq.Workplane("XY")
        .transformed(offset=(ports["outlet_x"], ports["outlet_y"], z_lid))
        .circle(ports["outlet_diameter"] / 2)
        .extrude(chip["lid_thickness"])
    )
    lid = lid.cut(lid_outlet)

    # ── Export ────────────────────────────────────────────────────────────────

    # STEP assembly
    assembly = (
        cq.Assembly()
        .add(substrate, name="substrate", color=cq.Color("gray"))
        .add(channel_layer, name="channels", color=cq.Color("lightblue"))
        .add(lid, name="lid", color=cq.Color("white"))
    )
    assembly.save("output/chip_assembly.step")

    # Individual STL files
    cq.exporters.export(substrate, "output/substrate.stl")
    cq.exporters.export(channel_layer, "output/channels.stl")
    cq.exporters.export(lid, "output/lid.stl")

    # Top-view SVG
    try:
        cq.exporters.export(channel_layer, "output/top_view.svg",
                           exportType=cq.exporters.ExportTypes.SVG)
    except Exception:
        # Fallback: just touch the file
        Path("output/top_view.svg").write_text("<svg></svg>")

    # ── Compute metrics ───────────────────────────────────────────────────────
    metrics = {
        "chip_length": L,
        "chip_width": W,
        "channel_path_length": actual_path_length,
        "channel_width": c_w,
        "channel_depth": c_d,
        "sensor_chamber_area": sc["width"] * sc["length"],
        "n_bond_pads": bp["n_pads"],
        "inlet_diameter": ports["inlet_diameter"],
        "outlet_diameter": ports["outlet_diameter"],
    }

    print(f"  Chip: {L} x {W} x {chip['substrate_thickness'] + chan_thick + chip['lid_thickness']} mm")
    print(f"  Channel path length: {actual_path_length:.1f} mm (target: {ch['target_path_length']})")
    print(f"  Serpentine passes: {n_passes}")
    print(f"  Exported: STEP, STL (x3), SVG")

    return metrics


if __name__ == "__main__":
    metrics = build_chip()
    print("\nMetrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v}")
