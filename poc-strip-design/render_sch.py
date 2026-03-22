#!/usr/bin/env python3
"""
render_sch.py — Parse xschem .sch files and render to PNG with proper
MOSFET symbols, wire routing, and net labels.

xschem sky130 MOSFET coordinate convention:
  - C line position (gx, gy) = gate pin location
  - mirror=0: channel is 20 units RIGHT of gate  (channel_x = gx + 20)
  - mirror=1: channel is 20 units LEFT of gate   (channel_x = gx - 20)
  - NFET: drain at (channel_x, gy - 30), source at (channel_x, gy + 30)
  - PFET: source at (channel_x, gy - 30), drain at (channel_x, gy + 30)
  - Screen coordinates: y_screen = -y_xschem (y is flipped)
"""
import os
import re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D


# ── xschem coordinate helpers ──────────────────────────────────────────────

GATE_OFFSET = 20   # gate-to-channel distance in xschem units
PIN_OFFSET = 30    # channel-center to drain/source distance


def mosfet_screen_coords(gx, gy, mirror):
    """Return screen coordinates for MOSFET terminals.

    Returns dict with keys: gate, channel, top, bot  (all in screen coords).
    'top' is drain for NFET, source for PFET (but the renderer doesn't
    need to distinguish — it just draws the symbol at the channel).
    """
    cx = gx - GATE_OFFSET if mirror == 1 else gx + GATE_OFFSET
    # screen y = -xschem_y
    return {
        'gate':    (gx, -gy),
        'channel': (cx, -gy),
        'top':     (cx, -(gy - PIN_OFFSET)),   # higher on screen (positive y)
        'bot':     (cx, -(gy + PIN_OFFSET)),   # lower on screen (negative y)
    }


# ── Drawing functions ──────────────────────────────────────────────────────

def draw_mosfet(ax, gx, gy, mirror=0, is_pmos=False, name="", w="", l=""):
    """Draw a clean MOSFET symbol using xschem coordinates.

    gx, gy: gate pin position (from C line, xschem coords).
    All drawing is in screen coords (y flipped).
    """
    t = mosfet_screen_coords(gx, gy, mirror)
    cx, cy = t['channel']
    gate_sx, gate_sy = t['gate']
    top_x, top_y = t['top']
    bot_x, bot_y = t['bot']

    # Gate direction in screen coords: gate is LEFT of channel (gdir=-1)
    # for mirror=0, RIGHT (gdir=+1) for mirror=1
    gdir = 1 if mirror == 1 else -1

    body_color = '#1a1a2e'
    nmos_color = '#1b7a3d'
    pmos_color = '#b71c1c'
    accent = pmos_color if is_pmos else nmos_color

    # ── Channel bar ──
    chan_h = 20  # half-height of drawn channel bar
    ax.plot([cx, cx], [cy - chan_h, cy + chan_h],
            color=body_color, linewidth=3.0, solid_capstyle='butt', zorder=5)

    # ── Three stub lines from channel to the gate-plate side ──
    gap = 4  # channel-to-plate gap
    plate_x = cx + gdir * gap
    stub_len = 5
    for dy in [-12, 0, 12]:
        ax.plot([cx, cx + gdir * stub_len], [cy + dy, cy + dy],
                color=body_color, linewidth=1.2, zorder=5)

    # ── Gate plate (vertical, parallel to channel) ──
    plate_h = 17
    ax.plot([plate_x, plate_x], [cy - plate_h, cy + plate_h],
            color=body_color, linewidth=2.5, solid_capstyle='round', zorder=5)

    # ── Gate connection line ──
    if is_pmos:
        # PMOS bubble
        br = 2.5
        bx = plate_x + gdir * br
        circle = plt.Circle((bx, cy), br, fill=False,
                             edgecolor=body_color, linewidth=1.5, zorder=6)
        ax.add_patch(circle)
        ax.plot([bx + gdir * br, gate_sx], [cy, gate_sy],
                color=body_color, linewidth=1.5, zorder=5)
    else:
        ax.plot([plate_x, gate_sx], [cy, gate_sy],
                color=body_color, linewidth=1.5, zorder=5)

    # ── Drain / source stubs ──
    ax.plot([cx, top_x], [cy + chan_h, top_y],
            color=body_color, linewidth=1.5, zorder=5)
    ax.plot([cx, bot_x], [cy - chan_h, bot_y],
            color=body_color, linewidth=1.5, zorder=5)

    # ── Arrow (NMOS: into channel on source side; PMOS: out on source side) ──
    arrow_dy = -8 if not is_pmos else 8
    arrow_y = cy + arrow_dy
    if is_pmos:
        ax.annotate('', xy=(cx + gdir * (gap - 0.5), arrow_y),
                    xytext=(cx, arrow_y),
                    arrowprops=dict(arrowstyle='->', color=accent,
                                   lw=1.5, mutation_scale=10),
                    zorder=6)
    else:
        ax.annotate('', xy=(cx, arrow_y),
                    xytext=(cx + gdir * (gap - 0.5), arrow_y),
                    arrowprops=dict(arrowstyle='->', color=accent,
                                   lw=1.5, mutation_scale=10),
                    zorder=6)

    # ── Terminal dots ──
    for tx, ty in [t['gate'], t['top'], t['bot']]:
        ax.plot(tx, ty, 'o', color=body_color, markersize=3, zorder=7)

    # ── Labels (on opposite side of gate) ──
    lab_dir = -gdir
    lx = cx + lab_dir * 22
    if name:
        ax.text(lx, cy + 6, name, fontsize=8, fontweight='bold',
                ha='center', va='bottom', color=accent, zorder=8)
    if w and l:
        ax.text(lx, cy - 4, f'W={w}\nL={l}', fontsize=5.5,
                ha='center', va='top', color='#666', zorder=8,
                linespacing=1.3)


def draw_label_pin(ax, x, y, label="", mirror=0):
    """Draw a net label badge at (x, -y) screen coords."""
    if not label:
        return
    sx, sy = x, -y

    if mirror == 1:
        ha, dx = 'right', -8
    else:
        ha, dx = 'left', 8

    # Color scheme by net type
    if label.upper() in ('VDD',):
        color, bg = '#b71c1c', '#fce4ec'
    elif label.upper() in ('GND', 'VSS'):
        color, bg = '#1a237e', '#e8eaf6'
    elif label.startswith('#'):
        return  # don't draw internal nets
    else:
        color, bg = '#e65100', '#fff3e0'

    ax.text(sx + dx, sy, label, fontsize=7, fontweight='bold',
            ha=ha, va='center', color=color,
            bbox=dict(facecolor=bg, edgecolor=color, alpha=0.92,
                      boxstyle='round,pad=0.25', linewidth=0.9),
            zorder=8)


# ── Main render function ──────────────────────────────────────────────────

def render_sch_to_png(filepath, output_path, title=None):
    """Render .sch file to PNG."""
    wires, components = parse_sch(filepath)

    if not wires and not components:
        print(f"  No geometry in {filepath}")
        return False

    fig, ax = plt.subplots(figsize=(16, 11))
    fig.patch.set_facecolor('white')

    all_x, all_y = [], []

    # ── Wires (drawn first, behind components) ──
    wire_labels_drawn = set()
    for x1, y1, x2, y2, label in wires:
        sy1, sy2 = -y1, -y2
        ax.plot([x1, x2], [sy1, sy2], color='#1976d2', linewidth=1.4,
                solid_capstyle='round', zorder=2)
        all_x.extend([x1, x2])
        all_y.extend([sy1, sy2])

        if label and not label.startswith('#') and label not in wire_labels_drawn:
            length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            if length > 25:
                mx, my = (x1 + x2) / 2, (sy1 + sy2) / 2
                ax.text(mx, my + 5, label, fontsize=5, ha='center',
                        va='bottom', color='#e65100', fontstyle='italic',
                        alpha=0.55, zorder=3)
                wire_labels_drawn.add(label)

    # ── Junction dots (3+ wires meet) ──
    endpoints = {}
    for x1, y1, x2, y2, _ in wires:
        for px, py in [(x1, -y1), (x2, -y2)]:
            key = (round(px, 1), round(py, 1))
            endpoints[key] = endpoints.get(key, 0) + 1
    for (px, py), cnt in endpoints.items():
        if cnt >= 3:
            ax.plot(px, py, 'o', color='#1976d2', markersize=4.5, zorder=4)

    # ── Components ──
    for comp in components:
        sym = comp['symbol'].lower()
        gx, gy = comp['x'], comp['y']
        mirror = comp['mirror']

        # Add terminal positions to bounds
        if 'fet' in sym or 'mos' in sym:
            t = mosfet_screen_coords(gx, gy, mirror)
            for v in t.values():
                all_x.append(v[0])
                all_y.append(v[1])
        else:
            all_x.append(gx)
            all_y.append(-gy)

        if 'nfet' in sym or 'nmos' in sym:
            draw_mosfet(ax, gx, gy, mirror=mirror, is_pmos=False,
                        name=comp['name'], w=comp['W'], l=comp['L'])
        elif 'pfet' in sym or 'pmos' in sym:
            draw_mosfet(ax, gx, gy, mirror=mirror, is_pmos=True,
                        name=comp['name'], w=comp['W'], l=comp['L'])
        elif any(k in sym for k in ('lab_pin', 'ipin', 'opin', 'iopin')):
            draw_label_pin(ax, gx, gy, label=comp['lab'], mirror=mirror)
        else:
            # Generic component box
            sx, sy = gx, -gy
            rect = FancyBboxPatch((sx - 10, sy - 8), 20, 16,
                                   boxstyle="round,pad=1.5",
                                   facecolor='#f5f5f5', edgecolor='#bdbdbd',
                                   linewidth=0.9, zorder=5)
            ax.add_patch(rect)
            short = sym.split('/')[-1][:8]
            ax.text(sx, sy, short, ha='center', va='center',
                    fontsize=5.5, color='#757575', zorder=6)

    if not all_x:
        plt.close()
        return False

    # ── Axes & styling ──
    margin = 45
    ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
    ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
    ax.set_aspect('equal')
    ax.set_facecolor('#fafbfc')
    ax.grid(True, alpha=0.05, color='#90a4ae', linewidth=0.5)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color('#cfd8dc')
        spine.set_linewidth(0.7)

    if title:
        ax.set_title(title, fontsize=14, fontweight='bold', pad=18,
                     color='#263238', fontfamily='sans-serif')

    # Legend
    legend_elements = [
        Line2D([0], [0], color='#1b7a3d', linewidth=2.5, label='NMOS'),
        Line2D([0], [0], color='#b71c1c', linewidth=2.5, label='PMOS'),
        Line2D([0], [0], color='#1976d2', linewidth=1.5, label='Wire'),
    ]
    leg = ax.legend(handles=legend_elements, loc='lower right', fontsize=8.5,
                    framealpha=0.95, edgecolor='#cfd8dc', fancybox=True)
    leg.get_frame().set_linewidth(0.7)

    # Stats badge
    n_mos = sum(1 for c in components
                if 'fet' in c['symbol'].lower() or 'mos' in c['symbol'].lower())
    n_pins = sum(1 for c in components if 'lab_pin' in c['symbol'].lower())
    stats = f"{n_mos} transistors  ·  {len(wires)} wires  ·  {n_pins} pins"
    ax.text(0.02, 0.02, stats, transform=ax.transAxes, fontsize=8,
            color='#78909c', fontfamily='sans-serif',
            bbox=dict(facecolor='white', alpha=0.92, edgecolor='#cfd8dc',
                      boxstyle='round,pad=0.3', linewidth=0.7))

    plt.tight_layout()
    plt.savefig(output_path, dpi=180, bbox_inches='tight',
                facecolor='white', pad_inches=0.25)
    plt.close()
    return True


# ── Parser ─────────────────────────────────────────────────────────────────

def parse_sch(filepath):
    """Parse xschem .sch file into wires and components."""
    wires, components = [], []

    with open(filepath) as f:
        content = f.read()

    comp_pattern = re.compile(
        r'C\s+\{([^}]+)\}\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)'
        r'\s+\{([^}]*)\}',
        re.DOTALL,
    )
    for m in comp_pattern.finditer(content):
        attrs = m.group(6)
        name_m = re.search(r'name=(\S+)', attrs)
        w_m = re.search(r'W=([\d.]+)', attrs)
        l_m = re.search(r'L=([\d.]+)', attrs)
        lab_m = re.search(r'lab=(\S+)', attrs)
        components.append({
            'symbol': m.group(1),
            'x': float(m.group(2)), 'y': float(m.group(3)),
            'rot': int(float(m.group(4))),
            'mirror': int(float(m.group(5))),
            'name': name_m.group(1) if name_m else "",
            'W': w_m.group(1) if w_m else "",
            'L': l_m.group(1) if l_m else "",
            'lab': lab_m.group(1) if lab_m else "",
        })

    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('N '):
            parts = line.split()
            if len(parts) >= 5:
                try:
                    x1, y1 = float(parts[1]), float(parts[2])
                    x2, y2 = float(parts[3]), float(parts[4])
                    lab_m = re.search(r'lab=(\S+)', line)
                    wires.append((x1, y1, x2, y2,
                                  lab_m.group(1) if lab_m else None))
                except ValueError:
                    pass

    return wires, components


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    circuits = {
        "current_mirror":
            "Cascode Current Mirror\nStable bias currents for all blocks",
        "transimpedance_amplifier":
            "Transimpedance Amplifier (TIA)\nConverts electrode current to voltage",
        "potentiostat":
            "Potentiostat Circuit\nControls electrode potential for SWV",
        "swv_generator":
            "SWV Waveform Generator\nStaircase + square pulse for voltammetry",
    }

    for name, desc in circuits.items():
        sch_path = f"schematics/{name}.sch"
        png_path = f"schematics/{name}.png"
        if os.path.exists(sch_path):
            print(f"Rendering {name}...")
            ok = render_sch_to_png(sch_path, png_path, title=desc)
            if ok:
                sz = os.path.getsize(png_path)
                print(f"  Saved: {png_path} ({sz:,} bytes)")
            else:
                print(f"  FAILED")
        else:
            print(f"  SKIP: {sch_path} not found")


if __name__ == "__main__":
    main()
