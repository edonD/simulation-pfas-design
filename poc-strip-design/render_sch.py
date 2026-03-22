#!/usr/bin/env python3
"""
render_sch.py — Parse xschem .sch files and render to PNG using matplotlib.

Reads wire (N) and component (C) lines from .sch files and draws them.
"""
import os
import re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle


def parse_sch(filepath):
    """Parse xschem .sch file, extract wires, components, and labels."""
    wires = []
    components = []
    labels = []

    with open(filepath) as f:
        content = f.read()

    for line in content.split('\n'):
        line = line.strip()

        # Wire: N x1 y1 x2 y2 {attributes}
        if line.startswith('N '):
            parts = line.split()
            if len(parts) >= 5:
                try:
                    x1, y1, x2, y2 = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
                    # Extract label if present
                    lab_match = re.search(r'lab=(\S+)', line)
                    label = lab_match.group(1) if lab_match else None
                    wires.append((x1, y1, x2, y2, label))
                except ValueError:
                    pass

        # Component: C {symbol} x y rotation mirror {attributes}
        elif line.startswith('C {'):
            match = re.match(r'C \{([^}]+)\}\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)', line)
            if match:
                symbol = match.group(1)
                x, y = float(match.group(2)), float(match.group(3))
                rot = float(match.group(4))
                mirror = float(match.group(5))
                # Extract name/value
                name_match = re.search(r'name=(\S+)', line)
                value_match = re.search(r'value=(\S+)', line)
                name = name_match.group(1) if name_match else ""
                value = value_match.group(1) if value_match else ""
                components.append((symbol, x, y, rot, mirror, name, value))

        # Text labels: T {text} x y ...
        elif line.startswith('T {'):
            match = re.match(r'T \{([^}]*)\}\s+([-\d.]+)\s+([-\d.]+)', line)
            if match:
                text = match.group(1)
                x, y = float(match.group(2)), float(match.group(3))
                labels.append((text, x, y))

    return wires, components, labels


def render_sch_to_png(filepath, output_path, title=None):
    """Render .sch file to PNG."""
    wires, components, labels = parse_sch(filepath)

    if not wires and not components:
        print(f"  No geometry in {filepath}")
        return False

    fig, ax = plt.subplots(figsize=(14, 10))

    # Collect all coordinates for bounds
    all_x = []
    all_y = []

    # Draw wires
    for x1, y1, x2, y2, label in wires:
        ax.plot([x1, x2], [-y1, -y2], color='#1565c0', linewidth=1.5, solid_capstyle='round')
        all_x.extend([x1, x2])
        all_y.extend([-y1, -y2])

        # Draw junction dots at wire intersections
        ax.plot(x1, -y1, 'o', color='#1565c0', markersize=3)
        ax.plot(x2, -y2, 'o', color='#1565c0', markersize=3)

        # Add wire labels for power/signal nets
        if label and label.startswith('#') is False:
            mx, my = (x1 + x2) / 2, -(y1 + y2) / 2
            ax.text(mx, my + 5, label, fontsize=6, ha='center', va='bottom',
                    color='#e65100', fontweight='bold',
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1))

    # Draw components
    for symbol, x, y, rot, mirror, name, value in components:
        # Draw component as a box
        sym_short = symbol.split('/')[-1] if '/' in symbol else symbol
        if 'nfet' in sym_short.lower() or 'nmos' in sym_short.lower():
            color = '#2e7d32'
            marker = 'N'
        elif 'pfet' in sym_short.lower() or 'pmos' in sym_short.lower():
            color = '#c62828'
            marker = 'P'
        elif 'res' in sym_short.lower():
            color = '#795548'
            marker = 'R'
        elif 'cap' in sym_short.lower():
            color = '#1565c0'
            marker = 'C'
        else:
            color = '#555'
            marker = sym_short[:3]

        rect = FancyBboxPatch((x - 15, -y - 15), 30, 30, boxstyle="round,pad=2",
                               facecolor=color, edgecolor='black', linewidth=1, alpha=0.3)
        ax.add_patch(rect)
        ax.text(x, -y, marker, ha='center', va='center', fontsize=8,
                fontweight='bold', color=color)

        # Component name below
        if name:
            ax.text(x, -y + 20, name, ha='center', va='top', fontsize=5, color='#333')

        all_x.append(x)
        all_y.append(-y)

    # Draw text labels
    for text, x, y in labels:
        ax.text(x, -y, text, fontsize=7, color='#333')
        all_x.append(x)
        all_y.append(-y)

    if not all_x:
        plt.close()
        return False

    # Set bounds with margin
    margin = 50
    ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
    ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.1)
    ax.set_xlabel('X', fontsize=9)
    ax.set_ylabel('Y', fontsize=9)

    if title:
        ax.set_title(title, fontsize=13, fontweight='bold')
    else:
        ax.set_title(os.path.basename(filepath), fontsize=13, fontweight='bold')

    # Stats annotation
    stats = f"Wires: {len(wires)} | Components: {len(components)} | Labels: {len(labels)}"
    ax.text(0.02, 0.02, stats, transform=ax.transAxes, fontsize=8,
            color='#555', bbox=dict(facecolor='white', alpha=0.8))

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    return True


def main():
    circuit_info = {
        "transimpedance_amplifier": "Transimpedance Amplifier (TIA)\nConverts electrode current to voltage for readout",
        "potentiostat": "Potentiostat Circuit\nControls electrode potential for SWV measurement",
        "swv_generator": "SWV Waveform Generator\nProduces staircase + square pulse for voltammetry",
        "current_mirror": "Cascode Current Mirror\nProvides stable bias currents for all analog blocks",
    }

    for name, desc in circuit_info.items():
        sch_path = f"schematics/{name}.sch"
        png_path = f"schematics/{name}.png"
        if os.path.exists(sch_path):
            print(f"Rendering {name}...")
            ok = render_sch_to_png(sch_path, png_path, title=desc)
            if ok:
                size = os.path.getsize(png_path)
                print(f"  Saved: {png_path} ({size} bytes)")
            else:
                print(f"  FAILED: no geometry found")
        else:
            print(f"  SKIP: {sch_path} not found")


if __name__ == "__main__":
    main()
