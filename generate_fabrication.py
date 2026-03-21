"""
generate_fabrication.py — Generate physical device layout and cross-section diagrams.

Creates:
  plots/07_device_layout.png        — Top-down chip layout
  plots/08_cross_section.png        — Cross-section of the sensor stack
  plots/09_fabrication_process.png  — Step-by-step fabrication flow
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Arc, Circle, Rectangle
from matplotlib.collections import PatchCollection

os.makedirs('plots', exist_ok=True)

# ── PLOT 7: Top-Down Device Layout ───────────────────────────────────────────
print("Generating Plot 7: Device Layout (Top-Down)...")
fig, ax = plt.subplots(figsize=(14, 10))
ax.set_xlim(0, 140)
ax.set_ylim(0, 100)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('PFAS Nanobiosensor — Physical Device Layout (Top View)\nChip size: ~5mm x 3.5mm',
             fontsize=14, fontweight='bold', pad=20)

# Chip outline
chip = FancyBboxPatch((5, 5), 130, 90, boxstyle="round,pad=2",
                       facecolor='#f0f0f0', edgecolor='black', linewidth=2)
ax.add_patch(chip)
ax.text(70, 97, 'Silicon / Glass Substrate', ha='center', fontsize=9, style='italic', color='gray')

# ── ZONE 1: Nanosensor Array (left) ──
sensor_zone = FancyBboxPatch((10, 25), 30, 55, boxstyle="round,pad=1",
                              facecolor='#c8e6c9', edgecolor='#2e7d32', linewidth=2)
ax.add_patch(sensor_zone)
ax.text(25, 82, 'NANOSENSOR\nARRAY', ha='center', fontsize=10, fontweight='bold', color='#1b5e20')
ax.text(25, 76, '(State: x)', ha='center', fontsize=8, color='#1b5e20')

# Draw sensor fingers (interdigitated electrodes)
for i in range(6):
    y_pos = 30 + i * 8
    ax.plot([14, 36], [y_pos, y_pos], color='#ffd700', linewidth=3, solid_capstyle='round')
    # Nanoparticle dots on electrodes
    for j in range(8):
        circle = plt.Circle((16 + j * 2.8, y_pos), 0.8, color='#e65100', alpha=0.7)
        ax.add_patch(circle)

ax.text(25, 27, 'Au electrodes +\nMIP nanoparticles', ha='center', fontsize=7, color='#555')

# ── ZONE 2: Microfluidic Channel (middle) ──
# Serpentine channel
channel_color = '#bbdefb'
channel_edge = '#1565c0'

# Draw serpentine
for i in range(4):
    y_base = 32 + i * 12
    ax.fill_between([42, 75], y_base - 2, y_base + 2, color=channel_color, alpha=0.6)
    ax.plot([42, 75], [y_base - 2, y_base - 2], color=channel_edge, linewidth=1.5)
    ax.plot([42, 75], [y_base + 2, y_base + 2], color=channel_edge, linewidth=1.5)
    if i < 3:
        side = 75 if i % 2 == 0 else 42
        ax.fill_between([side - 2, side + 2], y_base + 2, y_base + 10, color=channel_color, alpha=0.6)

ax.text(58, 82, 'MICROFLUIDIC\nDELAY CHANNEL', ha='center', fontsize=10, fontweight='bold', color='#0d47a1')
ax.text(58, 76, '(State: xd)', ha='center', fontsize=8, color='#0d47a1')
ax.text(58, 27, f'Serpentine PDMS\n\u03c4_d = 2.0 s delay', ha='center', fontsize=7, color='#555')

# Flow arrows
ax.annotate('', xy=(42, 55), xytext=(38, 55),
            arrowprops=dict(arrowstyle='->', color='#1565c0', lw=2))

# ── ZONE 3: Readout Electronics (right) ──
elec_zone = FancyBboxPatch((80, 25), 30, 55, boxstyle="round,pad=1",
                            facecolor='#fff3e0', edgecolor='#e65100', linewidth=2)
ax.add_patch(elec_zone)
ax.text(95, 82, 'READOUT\nELECTRONICS', ha='center', fontsize=10, fontweight='bold', color='#bf360c')
ax.text(95, 76, '(States: y, z, b)', ha='center', fontsize=8, color='#bf360c')

# Op-amp symbol
ax.plot([86, 86, 96, 86], [55, 65, 60, 55], color='#333', linewidth=2)
ax.text(88, 60, '+', fontsize=8, fontweight='bold')
ax.text(88, 57, '-', fontsize=8, fontweight='bold')

# Feedback loop
ax.annotate('', xy=(96, 60), xytext=(100, 60),
            arrowprops=dict(arrowstyle='->', color='#333', lw=1.5))
ax.plot([100, 100, 86, 86], [60, 68, 68, 65], color='#333', linewidth=1, linestyle='--')
ax.text(93, 70, 'feedback\n(2nd order)', fontsize=7, ha='center', color='#555')

# Capacitor and resistor symbols
ax.text(87, 48, 'R (damping \u03b6)', fontsize=7, color='#555')
ax.text(87, 44, 'C (frequency \u03c9n)', fontsize=7, color='#555')
ax.text(87, 40, 'DAC (burst b)', fontsize=7, color='#555')

ax.text(95, 27, 'CMOS ASIC\nAnalog front-end', ha='center', fontsize=7, color='#555')

# ── ZONE 4: Output Pads (far right) ──
for i, label in enumerate(['VDD', 'GND', 'OUT', 'CLK']):
    pad = FancyBboxPatch((115, 35 + i * 12), 12, 8, boxstyle="round,pad=0.5",
                          facecolor='#ffd700', edgecolor='#333', linewidth=1.5)
    ax.add_patch(pad)
    ax.text(121, 39 + i * 12, label, ha='center', fontsize=8, fontweight='bold')

ax.text(121, 82, 'BOND\nPADS', ha='center', fontsize=10, fontweight='bold', color='#555')

# ── Flow arrows between zones ──
ax.annotate('PFAS\nmolecules\nin fluid', xy=(10, 55), xytext=(-2, 55),
            fontsize=8, ha='right', color='#e65100', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='#e65100', lw=2))

ax.annotate('', xy=(80, 55), xytext=(76, 55),
            arrowprops=dict(arrowstyle='->', color='#1565c0', lw=2))

ax.annotate('', xy=(115, 55), xytext=(111, 55),
            arrowprops=dict(arrowstyle='->', color='#e65100', lw=2))

# ── Legend / Scale ──
ax.plot([10, 30], [10, 10], 'k-', linewidth=2)
ax.text(20, 7, '1 mm', ha='center', fontsize=9)
ax.text(70, 10, 'Total chip: ~5 mm x 3.5 mm (implantable form factor)', ha='center',
        fontsize=9, style='italic', color='gray')

plt.tight_layout()
plt.savefig('plots/07_device_layout.png', dpi=150, bbox_inches='tight')
plt.close()

# ── PLOT 8: Cross-Section ────────────────────────────────────────────────────
print("Generating Plot 8: Cross-Section...")
fig, ax = plt.subplots(figsize=(14, 8))
ax.set_xlim(0, 140)
ax.set_ylim(0, 80)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('PFAS Nanobiosensor — Cross-Section Through Sensor Region\n(Not to scale)',
             fontsize=14, fontweight='bold', pad=15)

layers = [
    (0, 0, 140, 12, '#d7ccc8', 'Silicon Substrate (500 \u00b5m)', 10),
    (0, 12, 140, 5, '#90a4ae', 'SiO\u2082 Insulation (200 nm)', 9),
    (10, 17, 25, 4, '#ffd700', 'Au Working Electrode (100 nm)', 8),
    (45, 17, 25, 4, '#c0c0c0', 'Ag/AgCl Reference (100 nm)', 8),
    (80, 17, 25, 4, '#ffd700', 'Au Counter Electrode (100 nm)', 8),
    (0, 21, 140, 3, '#e8eaf6', 'SAM Layer — thiol self-assembly (2 nm)', 7),
]

for x, y, w, h, color, label, fs in layers:
    rect = FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0",
                           facecolor=color, edgecolor='#333', linewidth=1)
    ax.add_patch(rect)

# Labels on the right
labels_right = [
    (6, 'Silicon Substrate (500 \u00b5m wafer)'),
    (14.5, 'SiO\u2082 Passivation (PECVD, 200 nm)'),
    (19, 'Metal Electrodes (e-beam Au, 100 nm)'),
    (22.5, 'SAM / Thiol Linker Layer (2 nm)'),
]
for y_pos, text in labels_right:
    ax.text(142, y_pos, text, fontsize=8, va='center', color='#333')
    ax.plot([138, 141], [y_pos, y_pos], 'k-', linewidth=0.5)

# MIP nanoparticles on electrodes
for x_center in [22, 57, 92]:
    for dx in [-8, -4, 0, 4, 8]:
        x_pos = x_center + dx
        # Nanoparticle
        circle = plt.Circle((x_pos, 26), 2.5, facecolor='#e65100', edgecolor='#bf360c',
                            linewidth=1, alpha=0.8)
        ax.add_patch(circle)
        # Binding sites (small bumps)
        for angle in [30, 90, 150]:
            bx = x_pos + 2.5 * np.cos(np.radians(angle))
            by = 26 + 2.5 * np.sin(np.radians(angle))
            dot = plt.Circle((bx, by), 0.5, facecolor='#1b5e20', alpha=0.8)
            ax.add_patch(dot)

ax.text(70, 30, 'MIP Nanoparticles (~50 nm)\nwith PFAS-selective binding sites',
        ha='center', fontsize=9, fontweight='bold', color='#bf360c')

# PFAS molecules approaching
for i in range(5):
    x_pos = 20 + i * 25
    # PFAS molecule (simplified as F-chain)
    ax.plot([x_pos, x_pos], [38, 45], color='#00bcd4', linewidth=2)
    ax.text(x_pos, 46, 'PFAS', ha='center', fontsize=6, color='#00838f')
    for j in range(4):
        ax.text(x_pos + 1.5, 39 + j * 1.8, 'F', fontsize=5, color='#00bcd4', fontweight='bold')
    ax.annotate('', xy=(x_pos, 33), xytext=(x_pos, 38),
                arrowprops=dict(arrowstyle='->', color='#00838f', lw=1))

# Fluid above
ax.fill_between([0, 140], 35, 80, color='#e1f5fe', alpha=0.3)
ax.text(70, 70, 'Interstitial Fluid / Blood Plasma', ha='center', fontsize=11,
        style='italic', color='#0277bd')

# PDMS channel walls
ax.fill_between([0, 5], 17, 60, color='#e0e0e0', alpha=0.8)
ax.fill_between([135, 140], 17, 60, color='#e0e0e0', alpha=0.8)
ax.text(2.5, 40, 'PDMS\nwall', ha='center', fontsize=7, color='#555', rotation=90)
ax.text(137.5, 40, 'PDMS\nwall', ha='center', fontsize=7, color='#555', rotation=90)

# Microfluidic channel label
ax.annotate('', xy=(5, 55), xytext=(135, 55),
            arrowprops=dict(arrowstyle='<->', color='#1565c0', lw=1.5))
ax.text(70, 57, 'Microfluidic channel height: 50-100 \u00b5m', ha='center', fontsize=8, color='#1565c0')

# Electrical connections
for x_pos, label in [(22, 'WE'), (57, 'RE'), (92, 'CE')]:
    ax.plot([x_pos, x_pos], [12, 7], color='#ffd700', linewidth=2)
    ax.text(x_pos, 4, label, ha='center', fontsize=8, fontweight='bold', color='#333')

ax.text(70, 1, 'To CMOS readout ASIC (wire bonds / TSV)', ha='center', fontsize=9,
        style='italic', color='#555')

plt.tight_layout()
plt.savefig('plots/08_cross_section.png', dpi=150, bbox_inches='tight')
plt.close()

# ── PLOT 9: Fabrication Process Flow ─────────────────────────────────────────
print("Generating Plot 9: Fabrication Process Flow...")
fig, axes = plt.subplots(2, 4, figsize=(18, 9))
fig.suptitle('Fabrication Process Flow — 8 Steps from Wafer to Implantable Sensor',
             fontsize=14, fontweight='bold')

steps = [
    ("Step 1: Substrate", "#d7ccc8",
     "Start with Si wafer\nor glass substrate\n(500 \u00b5m thick)\n\nClean: piranha + O\u2082 plasma"),
    ("Step 2: Insulation", "#90a4ae",
     "Deposit SiO\u2082 by\nPECVD (200 nm)\n\nPurpose: electrical\nisolation"),
    ("Step 3: Electrodes", "#ffd700",
     "E-beam evaporate\nTi/Au (10/100 nm)\n\nPattern by liftoff\nor wet etch"),
    ("Step 4: Microfluidics", "#bbdefb",
     "PDMS soft lithography:\n- SU-8 master mold\n- Cast PDMS\n- Plasma bond\n\nSerpentine for \u03c4_d=2s"),
    ("Step 5: SAM Layer", "#e8eaf6",
     "Self-assembled\nmonolayer (SAM)\nThiol chemistry\non Au surface\n\n12-24 hr incubation"),
    ("Step 6: Nanoparticles", "#e65100",
     "Deposit MIP\nnanoparticles\n(50 nm diameter)\n\nDrop-cast or\nelectrodeposition"),
    ("Step 7: ASIC Bond", "#fff3e0",
     "Wire-bond CMOS\nreadout chip\n\nAnalog front-end:\n- TIA + bandpass\n- 2nd-order filter\n- Burst DAC"),
    ("Step 8: Package", "#c8e6c9",
     "Biocompatible\nencapsulation\n\nParylene-C coating\n(except sensor window)\n\nSterilize: EtO gas"),
]

for idx, (title, color, desc) in enumerate(steps):
    ax = axes[idx // 4][idx % 4]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Background
    bg = FancyBboxPatch((0.5, 0.5), 9, 9, boxstyle="round,pad=0.3",
                         facecolor=color, edgecolor='#333', linewidth=1.5, alpha=0.3)
    ax.add_patch(bg)

    # Step number circle
    circle = plt.Circle((1.5, 8.5), 0.8, facecolor=color, edgecolor='#333', linewidth=2)
    ax.add_patch(circle)
    ax.text(1.5, 8.5, str(idx + 1), ha='center', va='center', fontsize=12, fontweight='bold')

    # Title
    ax.text(5.5, 8.5, title.replace(f"Step {idx+1}: ", ""), ha='center', va='center',
            fontsize=11, fontweight='bold')

    # Description
    ax.text(5, 4.5, desc, ha='center', va='center', fontsize=8,
            fontfamily='sans-serif', linespacing=1.4)

plt.tight_layout()
plt.savefig('plots/09_fabrication_process.png', dpi=150, bbox_inches='tight')
plt.close()

print("\nFabrication plots saved:")
print("  plots/07_device_layout.png")
print("  plots/08_cross_section.png")
print("  plots/09_fabrication_process.png")
