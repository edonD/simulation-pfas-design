"""
render.py — Generate 2D projection images of the 3D chip model.

Creates PNG renders from the exported SVG and additional matplotlib diagrams.
"""
import json, os, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle
from matplotlib.collections import PatchCollection

os.makedirs("plots", exist_ok=True)

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
c_w = ch["width"]
wall = ch["wall_spacing"]
r = ch["u_turn_radius"]

# Recompute serpentine geometry (same logic as model.py)
serp_x_start = sc["x_offset"] + sc["width"] + 0.2
serp_x_end = L - margin - 0.3
serp_y_min = margin + r
serp_y_max = W - margin - r
serp_width = serp_x_end - serp_x_start
pass_length = serp_y_max - serp_y_min
target_pl = ch["target_path_length"]
connection_overhead = 3.0
serpentine_budget = target_pl - connection_overhead
n_passes = max(2, round(serpentine_budget / (pass_length + c_w + wall)))
while n_passes * (c_w + wall) > serp_width + wall and n_passes > 2:
    n_passes -= 1

# Build path points (same as model.py)
path_points = []
chamber_exit_x = sc["x_offset"] + sc["width"]
chamber_exit_y = sc["y_offset"] + sc["length"] / 2
path_points.append((chamber_exit_x, chamber_exit_y))
path_points.append((serp_x_start, chamber_exit_y))
path_points.append((serp_x_start, serp_y_min))
current_y = serp_y_min
going_up = True

for i in range(n_passes):
    x_pos = serp_x_start + i * (c_w + wall)
    target_y = serp_y_max if going_up else serp_y_min
    path_points.append((x_pos, target_y))
    current_y = target_y
    if i < n_passes - 1:
        next_x = x_pos + c_w + wall
        path_points.append((next_x, current_y))
        going_up = not going_up

last_x, last_y = path_points[-1]
path_points.append((ports["outlet_x"], last_y))
path_points.append((ports["outlet_x"], ports["outlet_y"]))

# ── PLOT 1: Annotated Top View ───────────────────────────────────────────────
print("Generating annotated top view...")
fig, ax = plt.subplots(figsize=(14, 10))
ax.set_xlim(-0.5, L + 0.5)
ax.set_ylim(-0.5, W + 0.5)
ax.set_aspect('equal')

# Chip outline
chip_rect = FancyBboxPatch((0, 0), L, W, boxstyle="round,pad=0.05",
                            facecolor='#f5f5f5', edgecolor='black', linewidth=2)
ax.add_patch(chip_rect)

# Sensor chamber
chamber_rect = Rectangle((sc["x_offset"], sc["y_offset"]), sc["width"], sc["length"],
                           facecolor='#c8e6c9', edgecolor='#2e7d32', linewidth=1.5, alpha=0.7)
ax.add_patch(chamber_rect)
ax.text(sc["x_offset"] + sc["width"]/2, sc["y_offset"] + sc["length"]/2,
        'SENSOR\nCHAMBER', ha='center', va='center', fontsize=8, fontweight='bold', color='#1b5e20')

# Electrodes (interdigitated)
for i in range(elec["n_fingers"]):
    y_pos = sc["y_offset"] + 0.15 + i * (elec["finger_width"] + elec["finger_gap"])
    x_start = sc["x_offset"] + 0.15 + (0.2 if i % 2 else 0)
    finger = Rectangle((x_start, y_pos - elec["finger_width"]/2),
                        elec["finger_length"], elec["finger_width"],
                        facecolor='#ffd700', edgecolor='#b8860b', linewidth=0.5)
    ax.add_patch(finger)

# Serpentine channel
for j in range(len(path_points) - 1):
    x1, y1 = path_points[j]
    x2, y2 = path_points[j + 1]
    ax.plot([x1, x2], [y1, y2], color='#1565c0', linewidth=4, solid_capstyle='round', alpha=0.6)
    ax.plot([x1, x2], [y1, y2], color='#42a5f5', linewidth=2, solid_capstyle='round')

# Inlet connection
ax.plot([ports["inlet_x"], sc["x_offset"] + sc["width"]/2],
        [ports["inlet_y"], ports["inlet_y"]],
        color='#1565c0', linewidth=4, alpha=0.6)
ax.plot([ports["inlet_x"], sc["x_offset"] + sc["width"]/2],
        [ports["inlet_y"], ports["inlet_y"]],
        color='#42a5f5', linewidth=2)

# Ports
inlet_circle = Circle((ports["inlet_x"], ports["inlet_y"]), ports["inlet_diameter"]/2,
                       facecolor='#e3f2fd', edgecolor='#1565c0', linewidth=2)
outlet_circle = Circle((ports["outlet_x"], ports["outlet_y"]), ports["outlet_diameter"]/2,
                        facecolor='#fce4ec', edgecolor='#c62828', linewidth=2)
ax.add_patch(inlet_circle)
ax.add_patch(outlet_circle)
ax.text(ports["inlet_x"], ports["inlet_y"] + 0.4, 'INLET', ha='center', fontsize=8,
        fontweight='bold', color='#1565c0')
ax.text(ports["outlet_x"], ports["outlet_y"] + 0.4, 'OUTLET', ha='center', fontsize=8,
        fontweight='bold', color='#c62828')

# Bond pads
for i in range(bp["n_pads"]):
    y_pos = bp["y_start"] + i * bp["y_spacing"]
    pad = Rectangle((bp["x_position"] - bp["pad_width"]/2, y_pos - bp["pad_height"]/2),
                     bp["pad_width"], bp["pad_height"],
                     facecolor='#ffd700', edgecolor='#333', linewidth=1.5)
    ax.add_patch(pad)
    label = bp["labels"][i] if i < len(bp["labels"]) else f"P{i}"
    ax.text(bp["x_position"], y_pos, label, ha='center', va='center', fontsize=6, fontweight='bold')

# Annotations
ax.annotate(f'Chip: {L} x {W} mm', xy=(L/2, -0.3), fontsize=11, ha='center', fontweight='bold')

# Dimension arrows
ax.annotate('', xy=(L, -0.15), xytext=(0, -0.15),
            arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
ax.text(L/2, -0.25, f'{L} mm', ha='center', fontsize=9)

ax.annotate('', xy=(-0.15, W), xytext=(-0.15, 0),
            arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
ax.text(-0.35, W/2, f'{W} mm', ha='center', fontsize=9, rotation=90)

# Flow direction
ax.annotate('Flow', xy=(2.5, 1.75), xytext=(0.2, 0.3),
            fontsize=10, color='#1565c0', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='#1565c0', lw=2))

ax.set_xlabel('X (mm)', fontsize=11)
ax.set_ylabel('Y (mm)', fontsize=11)
ax.set_title('PFAS Nanobiosensor Microfluidic Chip — Top View\n(CadQuery 3D Model)',
             fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig('plots/cad_top_view.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved: plots/cad_top_view.png")

# ── PLOT 2: Exploded Layer View ──────────────────────────────────────────────
print("Generating exploded layer view...")
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')

# Draw each layer as a slab with vertical separation
layer_colors = ['#d7ccc8', '#ffd700', '#bbdefb', '#e0e0e0']
layer_names = ['1. Silicon Substrate\n   (0.5 mm)', '2. Electrodes\n   (Au, 100 nm)',
               '3. PDMS Channel Layer\n   (1.0 mm)', '4. Glass Lid\n   (0.2 mm)']
layer_z = [0, 2, 4, 7]
layer_thick = [0.5, 0.05, 1.0, 0.2]

for i, (z_base, thick, color, name) in enumerate(zip(layer_z, layer_thick, layer_colors, layer_names)):
    # Draw rectangular prism faces
    xs = [0, L, L, 0, 0]
    ys = [0, 0, W, W, 0]

    # Bottom face
    ax.plot_surface(
        np.array([[0, L], [0, L]]),
        np.array([[0, 0], [W, W]]),
        np.array([[z_base, z_base], [z_base, z_base]]),
        color=color, alpha=0.7, edgecolor='#333', linewidth=0.5
    )
    # Top face
    ax.plot_surface(
        np.array([[0, L], [0, L]]),
        np.array([[0, 0], [W, W]]),
        np.array([[z_base+thick, z_base+thick], [z_base+thick, z_base+thick]]),
        color=color, alpha=0.7, edgecolor='#333', linewidth=0.5
    )
    # Side faces
    for (x1, y1, x2, y2) in [(0,0,L,0), (L,0,L,W), (L,W,0,W), (0,W,0,0)]:
        ax.plot_surface(
            np.array([[x1, x2], [x1, x2]]),
            np.array([[y1, y2], [y1, y2]]),
            np.array([[z_base, z_base], [z_base+thick, z_base+thick]]),
            color=color, alpha=0.4, edgecolor='#333', linewidth=0.3
        )

    # Label
    ax.text(L + 0.5, W/2, z_base + thick/2, name, fontsize=8, color='#333')

# Draw serpentine on channel layer
z_ch = 4 + 0.05
for j in range(len(path_points) - 1):
    x1, y1 = path_points[j]
    x2, y2 = path_points[j + 1]
    ax.plot([x1, x2], [y1, y2], [z_ch, z_ch], color='#1565c0', linewidth=2, alpha=0.8)

# Ports
for px, py, label in [(ports["inlet_x"], ports["inlet_y"], "IN"),
                       (ports["outlet_x"], ports["outlet_y"], "OUT")]:
    ax.plot([px, px], [py, py], [4, 8], color='#c62828', linewidth=2, linestyle='--', alpha=0.5)
    ax.text(px, py, 8.2, label, fontsize=8, ha='center', color='#c62828', fontweight='bold')

ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
ax.set_zlabel('Layer stack')
ax.set_title('Exploded Layer View — 4 Stacked Layers', fontsize=13, fontweight='bold')
ax.view_init(elev=25, azim=-50)
ax.set_xlim(0, L+1)
ax.set_ylim(0, W+1)

plt.tight_layout()
plt.savefig('plots/cad_exploded_view.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved: plots/cad_exploded_view.png")

# ── PLOT 3: Serpentine Channel Detail ────────────────────────────────────────
print("Generating serpentine detail...")
fig, ax = plt.subplots(figsize=(10, 8))
ax.set_aspect('equal')

# Draw channel path with width
for j in range(len(path_points) - 1):
    x1, y1 = path_points[j]
    x2, y2 = path_points[j + 1]

    if abs(x2 - x1) < 0.001:  # vertical
        rect = Rectangle((x1 - c_w/2, min(y1,y2)), c_w, abs(y2-y1),
                          facecolor='#bbdefb', edgecolor='#1565c0', linewidth=1)
    else:  # horizontal
        rect = Rectangle((min(x1,x2), y1 - c_w/2), abs(x2-x1), c_w,
                          facecolor='#bbdefb', edgecolor='#1565c0', linewidth=1)
    ax.add_patch(rect)

# Centerline
for j in range(len(path_points) - 1):
    x1, y1 = path_points[j]
    x2, y2 = path_points[j + 1]
    ax.plot([x1, x2], [y1, y2], 'b--', linewidth=0.5, alpha=0.5)

# Calculate actual path length
actual_path = 0
for j in range(len(path_points) - 1):
    x1, y1 = path_points[j]
    x2, y2 = path_points[j + 1]
    actual_path += math.sqrt((x2-x1)**2 + (y2-y1)**2)

# Sensor chamber
chamber_rect = Rectangle((sc["x_offset"], sc["y_offset"]), sc["width"], sc["length"],
                           facecolor='#c8e6c9', edgecolor='#2e7d32', linewidth=2, alpha=0.5)
ax.add_patch(chamber_rect)
ax.text(sc["x_offset"] + sc["width"]/2, sc["y_offset"] + sc["length"]/2,
        'Sensor\nChamber', ha='center', va='center', fontsize=9, fontweight='bold', color='#1b5e20')

# Dimensions
ax.annotate(f'Channel width:\n{c_w*1000:.0f} \u00b5m', xy=(serp_x_start + 0.1, serp_y_max + 0.15),
            fontsize=9, color='#1565c0', fontweight='bold')
ax.annotate(f'Wall spacing:\n{wall*1000:.0f} \u00b5m', xy=(serp_x_start + c_w + 0.02, serp_y_max/2),
            fontsize=8, color='#555')
ax.text(serp_x_start + n_passes*(c_w+wall)/2, -0.2,
        f'Total path length: {actual_path:.1f} mm ({n_passes} serpentine passes)',
        ha='center', fontsize=10, fontweight='bold', color='#1565c0')

# Flow arrows along the path
for j in range(0, len(path_points) - 1, 2):
    x1, y1 = path_points[j]
    x2, y2 = path_points[j + 1]
    mx, my = (x1+x2)/2, (y1+y2)/2
    dx, dy = x2-x1, y2-y1
    norm = max(math.sqrt(dx*dx+dy*dy), 0.001)
    ax.annotate('', xy=(mx+dx/norm*0.15, my+dy/norm*0.15),
                xytext=(mx-dx/norm*0.15, my-dy/norm*0.15),
                arrowprops=dict(arrowstyle='->', color='#e65100', lw=1.5))

ax.set_xlim(sc["x_offset"] - 0.3, ports["outlet_x"] + 0.5)
ax.set_ylim(-0.5, W + 0.3)
ax.set_xlabel('X (mm)', fontsize=11)
ax.set_ylabel('Y (mm)', fontsize=11)
ax.set_title('Serpentine Delay Channel — Detail View\n(provides \u03c4_d = 2.0 s transport delay)',
             fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig('plots/cad_serpentine_detail.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved: plots/cad_serpentine_detail.png")

# ── PLOT 4: Cross-section rendering ──────────────────────────────────────────
print("Generating cross-section...")
fig, ax = plt.subplots(figsize=(14, 6))
ax.set_xlim(-0.5, L + 0.5)
ax.set_ylim(-0.2, 2.2)
ax.set_aspect('auto')

# Substrate
ax.fill_between([0, L], 0, 0.5, color='#d7ccc8', edgecolor='#333', linewidth=1)
ax.text(L/2, 0.25, 'Silicon Substrate (500 \u00b5m)', ha='center', fontsize=9, color='#555')

# Electrodes on top of substrate
for x_pos in [0.8, 1.2, 1.6]:
    ax.fill_between([x_pos-0.15, x_pos+0.15], 0.5, 0.52, color='#ffd700', edgecolor='#b8860b', linewidth=1)

# PDMS channel layer
ax.fill_between([0, L], 0.5, 1.5, color='#e3f2fd', edgecolor='#333', linewidth=1, alpha=0.7)

# Channel cuts in PDMS
for j in range(len(path_points) - 1):
    x1, y1 = path_points[j]
    x2, y2 = path_points[j + 1]
    if abs(y2 - y1) < 0.001:  # horizontal segment visible in cross-section
        ax.fill_between([min(x1,x2), max(x1,x2)], 0.5, 0.6, color='white', edgecolor='#1565c0', linewidth=0.5)

# Sensor chamber
ax.fill_between([sc["x_offset"], sc["x_offset"]+sc["width"]], 0.5, 0.6,
                color='#c8e6c9', edgecolor='#2e7d32', linewidth=1)
ax.text(sc["x_offset"]+sc["width"]/2, 0.55, 'Sensor\nChamber', ha='center', fontsize=7, color='#1b5e20')

ax.text(L/2, 1.0, 'PDMS Channel Layer (1.0 mm)', ha='center', fontsize=9, color='#1565c0')

# Lid
ax.fill_between([0, L], 1.5, 1.7, color='#e0e0e0', edgecolor='#333', linewidth=1, alpha=0.8)
ax.text(L/2, 1.6, 'Glass Lid (200 \u00b5m)', ha='center', fontsize=9, color='#555')

# Inlet/outlet ports
for px, label in [(ports["inlet_x"], 'IN'), (ports["outlet_x"], 'OUT')]:
    ax.fill_between([px-0.12, px+0.12], 0.6, 1.7, color='white', edgecolor='#c62828', linewidth=1, linestyle='--')
    ax.text(px, 1.85, label, ha='center', fontsize=8, fontweight='bold', color='#c62828')
    ax.annotate('', xy=(px, 1.75), xytext=(px, 2.05),
                arrowprops=dict(arrowstyle='->', color='#1565c0', lw=1.5))

# Bond pads
for i in range(bp["n_pads"]):
    ax.fill_between([bp["x_position"]-0.1, bp["x_position"]+0.1], 0.5, 0.52, color='#ffd700')

ax.text(bp["x_position"], 0.42, 'Bond\nPads', ha='center', fontsize=7, color='#333')

ax.set_xlabel('X position along chip (mm)', fontsize=11)
ax.set_ylabel('Height (mm)', fontsize=11)
ax.set_title('Cross-Section View (Y = 1.75 mm, through inlet/outlet axis)',
             fontsize=13, fontweight='bold')

plt.tight_layout()
plt.savefig('plots/cad_cross_section.png', dpi=150, bbox_inches='tight')
plt.close()
print("  Saved: plots/cad_cross_section.png")

print("\nAll CAD visualization plots saved to plots/")
