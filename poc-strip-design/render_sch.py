#!/usr/bin/env python3
"""
render_sch.py — Parse xschem .sch files and render to PNG with proper
MOSFET symbols, wire routing, and net labels.
"""
import os
import re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Arc
from matplotlib.lines import Line2D


def parse_sch(filepath):
    """Parse xschem .sch file."""
    wires = []
    components = []

    with open(filepath) as f:
        content = f.read()

    # Parse multi-line component blocks: C {symbol} x y rot mirror {attrs\n...\n}
    # Components can span multiple lines
    comp_pattern = re.compile(
        r'C\s+\{([^}]+)\}\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+\{([^}]*)\}',
        re.DOTALL
    )
    for m in comp_pattern.finditer(content):
        symbol = m.group(1)
        x, y = float(m.group(2)), float(m.group(3))
        rot = int(float(m.group(4)))
        mirror = int(float(m.group(5)))
        attrs = m.group(6)

        name_m = re.search(r'name=(\S+)', attrs)
        name = name_m.group(1) if name_m else ""
        w_m = re.search(r'W=([\d.]+)', attrs)
        l_m = re.search(r'L=([\d.]+)', attrs)
        w_val = w_m.group(1) if w_m else ""
        l_val = l_m.group(1) if l_m else ""
        lab_m = re.search(r'lab=(\S+)', attrs)
        lab = lab_m.group(1) if lab_m else ""

        components.append({
            'symbol': symbol, 'x': x, 'y': y,
            'rot': rot, 'mirror': mirror,
            'name': name, 'W': w_val, 'L': l_val, 'lab': lab,
        })

    # Parse wires
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('N '):
            parts = line.split()
            if len(parts) >= 5:
                try:
                    x1, y1, x2, y2 = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
                    lab_m = re.search(r'lab=(\S+)', line)
                    label = lab_m.group(1) if lab_m else None
                    wires.append((x1, y1, x2, y2, label))
                except ValueError:
                    pass

    return wires, components


def draw_nmos(ax, x, y, mirror=0, name="", w="", l="", scale=1.0):
    """Draw NMOS transistor symbol at (x, y).
    Standard xschem orientation: gate on left, drain top, source bottom.
    mirror=1 means gate on right.
    """
    s = 12 * scale  # symbol half-size

    if mirror == 1:
        gx = 1  # gate direction (right)
    else:
        gx = -1  # gate direction (left)

    # Channel line (vertical)
    ax.plot([x, x], [y - s, y + s], color='#1a1a1a', linewidth=2, solid_capstyle='butt')

    # Gate line (horizontal stub + vertical plate)
    gate_x = x + gx * s * 0.6
    ax.plot([gate_x, gate_x], [y - s * 0.7, y + s * 0.7], color='#1a1a1a', linewidth=2.5)
    ax.plot([gate_x, x + gx * s * 1.2], [y, y], color='#1a1a1a', linewidth=1.5)

    # Drain (top)
    ax.plot([x, x], [y + s, y + s * 1.5], color='#1a1a1a', linewidth=1.5)
    # Source (bottom)
    ax.plot([x, x], [y - s, y - s * 1.5], color='#1a1a1a', linewidth=1.5)

    # Arrow on source (pointing into channel for NMOS)
    ax.annotate('', xy=(x, y - s * 0.3), xytext=(x + gx * s * 0.55, y - s * 0.3),
                arrowprops=dict(arrowstyle='->', color='#1a1a1a', lw=1.2))

    # Body connection line
    ax.plot([x, x + gx * s * 0.6], [y - s * 0.3, y - s * 0.3], color='#1a1a1a', linewidth=0.8, alpha=0.5)
    ax.plot([x, x + gx * s * 0.6], [y + s * 0.3, y + s * 0.3], color='#1a1a1a', linewidth=0.8, alpha=0.5)

    # Label
    label_x = x - gx * s * 0.8
    if name:
        ax.text(label_x, y + s * 0.3, name, fontsize=7, fontweight='bold',
                ha='center', va='bottom', color='#2e7d32')
    if w and l:
        ax.text(label_x, y - s * 0.3, f'W={w}\nL={l}', fontsize=5,
                ha='center', va='top', color='#555')


def draw_pmos(ax, x, y, mirror=0, name="", w="", l="", scale=1.0):
    """Draw PMOS transistor symbol at (x, y)."""
    s = 12 * scale

    if mirror == 1:
        gx = 1
    else:
        gx = -1

    # Channel line
    ax.plot([x, x], [y - s, y + s], color='#1a1a1a', linewidth=2, solid_capstyle='butt')

    # Gate with bubble (PMOS indicator)
    gate_x = x + gx * s * 0.6
    ax.plot([gate_x, gate_x], [y - s * 0.7, y + s * 0.7], color='#1a1a1a', linewidth=2.5)
    bubble_x = gate_x + gx * s * 0.2
    circle = plt.Circle((bubble_x, y), s * 0.12, fill=False, edgecolor='#1a1a1a', linewidth=1.5)
    ax.add_patch(circle)
    ax.plot([bubble_x + gx * s * 0.12, x + gx * s * 1.2], [y, y], color='#1a1a1a', linewidth=1.5)

    # Drain (top)
    ax.plot([x, x], [y + s, y + s * 1.5], color='#1a1a1a', linewidth=1.5)
    # Source (bottom)
    ax.plot([x, x], [y - s, y - s * 1.5], color='#1a1a1a', linewidth=1.5)

    # Arrow on source (pointing out of channel for PMOS)
    ax.annotate('', xy=(x + gx * s * 0.55, y + s * 0.3), xytext=(x, y + s * 0.3),
                arrowprops=dict(arrowstyle='->', color='#1a1a1a', lw=1.2))

    # Body connections
    ax.plot([x, x + gx * s * 0.6], [y - s * 0.3, y - s * 0.3], color='#1a1a1a', linewidth=0.8, alpha=0.5)
    ax.plot([x, x + gx * s * 0.6], [y + s * 0.3, y + s * 0.3], color='#1a1a1a', linewidth=0.8, alpha=0.5)

    # Label
    label_x = x - gx * s * 0.8
    if name:
        ax.text(label_x, y + s * 0.3, name, fontsize=7, fontweight='bold',
                ha='center', va='bottom', color='#c62828')
    if w and l:
        ax.text(label_x, y - s * 0.3, f'W={w}\nL={l}', fontsize=5,
                ha='center', va='top', color='#555')


def draw_label_pin(ax, x, y, label="", mirror=0):
    """Draw a label/pin marker."""
    if not label:
        return
    s = 8
    if mirror == 1:
        ha = 'right'
        dx = -s
    else:
        ha = 'left'
        dx = s

    color = '#e65100'
    if label in ('VDD', 'vdd'):
        color = '#c62828'
    elif label in ('GND', 'VSS', 'vss', 'gnd'):
        color = '#1a237e'
    elif label.startswith('#'):
        color = '#666'

    ax.text(x + dx, y, label, fontsize=6, fontweight='bold',
            ha=ha, va='center', color=color,
            bbox=dict(facecolor='white', edgecolor=color, alpha=0.8,
                      boxstyle='round,pad=0.15', linewidth=0.8))


def render_sch_to_png(filepath, output_path, title=None):
    """Render .sch file to PNG with proper circuit symbols."""
    wires, components = parse_sch(filepath)

    if not wires and not components:
        print(f"  No geometry in {filepath}")
        return False

    fig, ax = plt.subplots(figsize=(14, 10))

    all_x = []
    all_y = []

    # Draw wires first (behind components)
    wire_labels_drawn = set()
    for x1, y1, x2, y2, label in wires:
        # Flip Y (xschem Y is inverted)
        py1, py2 = -y1, -y2
        ax.plot([x1, x2], [py1, py2], color='#1565c0', linewidth=1.2,
                solid_capstyle='round', zorder=1)
        all_x.extend([x1, x2])
        all_y.extend([py1, py2])

        # Draw net label once per unique label (avoid clutter)
        if label and not label.startswith('#') and label not in wire_labels_drawn:
            mx, my = (x1 + x2) / 2, (py1 + py2) / 2
            # Only label horizontal or long wires
            length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            if length > 15:
                ax.text(mx, my + 4, label, fontsize=5, ha='center', va='bottom',
                        color='#e65100', fontstyle='italic', alpha=0.7)
                wire_labels_drawn.add(label)

    # Draw junction dots where 3+ wires meet
    wire_endpoints = {}
    for x1, y1, x2, y2, _ in wires:
        for px, py in [(x1, -y1), (x2, -y2)]:
            key = (round(px, 1), round(py, 1))
            wire_endpoints[key] = wire_endpoints.get(key, 0) + 1
    for (px, py), count in wire_endpoints.items():
        if count >= 3:
            ax.plot(px, py, 'o', color='#1565c0', markersize=4, zorder=3)

    # Draw components
    for comp in components:
        sym = comp['symbol'].lower()
        x, y = comp['x'], -comp['y']  # flip Y
        mirror = comp['mirror']
        name = comp['name']
        w = comp['W']
        l = comp['L']
        lab = comp['lab']

        all_x.append(x)
        all_y.append(y)

        if 'nfet' in sym or 'nmos' in sym:
            draw_nmos(ax, x, y, mirror=mirror, name=name, w=w, l=l)
        elif 'pfet' in sym or 'pmos' in sym:
            draw_pmos(ax, x, y, mirror=mirror, name=name, w=w, l=l)
        elif 'lab_pin' in sym or 'ipin' in sym or 'opin' in sym or 'iopin' in sym:
            draw_label_pin(ax, x, y, label=lab, mirror=mirror)
        elif 'res' in sym:
            # Resistor: zigzag
            s = 10
            ax.plot([x, x], [y - s * 1.5, y + s * 1.5], color='#795548', linewidth=2)
            for i in range(5):
                yi = y - s + i * s * 0.4
                ax.plot([x - 4, x + 4], [yi, yi + s * 0.2], color='#795548', linewidth=1.5)
            if name:
                ax.text(x + 10, y, name, fontsize=6, color='#795548')
        elif 'cap' in sym:
            # Capacitor: two parallel lines
            s = 8
            ax.plot([x - 6, x + 6], [y + 2, y + 2], color='#1565c0', linewidth=2.5)
            ax.plot([x - 6, x + 6], [y - 2, y - 2], color='#1565c0', linewidth=2.5)
            ax.plot([x, x], [y + 2, y + s], color='#1565c0', linewidth=1.5)
            ax.plot([x, x], [y - 2, y - s], color='#1565c0', linewidth=1.5)
            if name:
                ax.text(x + 10, y, name, fontsize=6, color='#1565c0')
        else:
            # Generic: small rectangle
            rect = FancyBboxPatch((x - 8, y - 8), 16, 16, boxstyle="round,pad=1",
                                   facecolor='#eee', edgecolor='#999', linewidth=0.8, zorder=2)
            ax.add_patch(rect)
            short = sym.split('/')[-1][:6]
            ax.text(x, y, short, ha='center', va='center', fontsize=5, color='#555')

    if not all_x:
        plt.close()
        return False

    margin = 30
    ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
    ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
    ax.set_aspect('equal')
    ax.set_facecolor('#fafafa')
    ax.grid(True, alpha=0.08, color='#999')

    # Remove axis labels for cleaner look
    ax.set_xticks([])
    ax.set_yticks([])

    if title:
        ax.set_title(title, fontsize=13, fontweight='bold', pad=15)

    # Legend
    legend_elements = [
        Line2D([0], [0], color='#2e7d32', linewidth=2, label='NMOS'),
        Line2D([0], [0], color='#c62828', linewidth=2, label='PMOS'),
        Line2D([0], [0], color='#1565c0', linewidth=1.5, label='Wire'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=8, framealpha=0.9)

    # Stats
    n_mos = sum(1 for c in components if 'fet' in c['symbol'].lower())
    n_pins = sum(1 for c in components if 'lab_pin' in c['symbol'].lower())
    stats = f"{n_mos} transistors | {len(wires)} wires | {n_pins} pins"
    ax.text(0.02, 0.02, stats, transform=ax.transAxes, fontsize=8,
            color='#555', bbox=dict(facecolor='white', alpha=0.8, edgecolor='#ddd'))

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return True


def main():
    circuits = {
        "transimpedance_amplifier": "Transimpedance Amplifier (TIA)\nConverts electrode current to voltage",
        "potentiostat": "Potentiostat Circuit\nControls electrode potential for SWV",
        "swv_generator": "SWV Waveform Generator\nStaircase + square pulse for voltammetry",
        "current_mirror": "Cascode Current Mirror\nStable bias currents for all blocks",
    }

    for name, desc in circuits.items():
        sch_path = f"schematics/{name}.sch"
        png_path = f"schematics/{name}.png"
        if os.path.exists(sch_path):
            print(f"Rendering {name}...")
            ok = render_sch_to_png(sch_path, png_path, title=desc)
            if ok:
                print(f"  Saved: {png_path} ({os.path.getsize(png_path)} bytes)")
            else:
                print(f"  FAILED")
        else:
            print(f"  SKIP: {sch_path} not found")


if __name__ == "__main__":
    main()
