"""EE347 Task 3.2.7 — theoretical 208-V transformer-bank loading.

Run in Spyder or with: python EE347_Transformer_Gradient_Heatmap.py
Dependencies: numpy and matplotlib (available in standard Spyder setups).

Creates one PNG gradient heatmap and an overload-only CSV.

MODELING NOTE: PF=0.95 is a chosen LAGGING INPUT power-factor assumption;
it is NOT implied by a manufacturer's reported 4.7% VFD relative loss.
For a real VFD, harmonics and VFD-input measurements matter.
"""
from pathlib import Path
import csv
import math
from itertools import product

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize

# ------------ Change these inputs as desired -----------------
V_LL = 208.0                         # 3-phase transformer secondary line-to-line V
FREQUENCY_HZ = 60.0                  # source frequency
TRANSFORMER_VA = 3 * 250.0          # 3 x 250 VA delta-delta transformers
RPM = 1770.0                        # fixed hypothetical shaft speed
PF_VFD_INPUT = 0.95                 # chosen lagging input power factor
MOTOR_EFF = 1.00                    # idealized efficiency
VFD_EFF = 1.00                      # idealized efficiency
TORQUE_MIN_NM = 0.0
TORQUE_MAX_NM = 1.25
TORQUE_SAMPLES = 301                 # fine torque sweep for smooth appearance
RESISTANCES_OHM = (1200.0, 600.0, 300.0)     # per phase, wye
CAPACITANCES_UF = (2.2, 4.4, 8.8)           # per branch, delta
MOTOR_RATED_OUTPUT_W = 175.0
DYNAMOMETER_RATED_OUTPUT_W = 350.0
# -------------------------------------------------------------

OUTPUT_DIR = Path(__file__).resolve().parent if '__file__' in globals() else Path.cwd()
PNG_FILE = OUTPUT_DIR / 'EE347_Transformer_Gradient_Heatmap.png'
CSV_FILE = OUTPUT_DIR / 'EE347_Heatmap_Overloads_Only.csv'


def subset_label(flags, values, unit=''):
    items = [f'{v:g}' for flag, v in zip(flags, values) if flag]
    return '+'.join(items) if items else 'none'


def make_heatmap():
    if not (0 < PF_VFD_INPUT <= 1):
        raise ValueError('Input PF must be in (0, 1].')
    if MOTOR_EFF <= 0 or VFD_EFF <= 0:
        raise ValueError('Efficiencies must be positive.')
    if TORQUE_MIN_NM < 0 or TORQUE_MAX_NM <= TORQUE_MIN_NM:
        raise ValueError('Invalid torque range.')

    torques = np.linspace(TORQUE_MIN_NM, TORQUE_MAX_NM, TORQUE_SAMPLES)
    shaft_w = torques * (2 * math.pi * RPM / 60.0)
    p_vfd = shaft_w / (MOTOR_EFF * VFD_EFF)
    q_vfd = p_vfd * math.tan(math.acos(PF_VFD_INPUT))  # positive: lagging

    resistor_states = list(product((False, True), repeat=3))
    capacitor_states = list(product((False, True), repeat=3))
    # Each section contains eight resistor choices at one fixed capacitor choice.
    # Sort by number / size of enabled steps to make the map easier to read.
    resistor_states.sort(key=lambda flags: sum(1 / r for flag, r in zip(flags, RESISTANCES_OHM) if flag))
    capacitor_states.sort(key=lambda flags: sum(c for flag, c in zip(flags, CAPACITANCES_UF) if flag))

    configurations = []
    for c_flags in capacitor_states:
        for r_flags in resistor_states:
            p_r = sum(V_LL ** 2 / r for on, r in zip(r_flags, RESISTANCES_OHM) if on)
            q_c = -3 * V_LL ** 2 * 2 * math.pi * FREQUENCY_HZ * sum(
                c * 1e-6 for on, c in zip(c_flags, CAPACITANCES_UF) if on
            )
            configurations.append((r_flags, c_flags, p_r, q_c))

    # Algebraically add the signed P and Q at the modeled source-side bus.
    p_total = np.array([row[2] for row in configurations])[:, None] + p_vfd[None, :]
    q_total = np.array([row[3] for row in configurations])[:, None] + q_vfd[None, :]
    apparent_va = np.hypot(p_total, q_total)
    current_a = apparent_va / (math.sqrt(3) * V_LL)
    loading_pct = 100 * apparent_va / TRANSFORMER_VA

    # Color transition: green -> yellow -> orange near 98-100% -> red above 100%.
    vmax = max(125, math.ceil(float(loading_pct.max()) / 5) * 5)
    steps = [
        (0.0, '#247349'),
        (70.0, '#48ab70'),
        (85.0, '#c4df86'),
        (94.0, '#f7df72'),
        (98.0, '#f5a53b'),
        (100.0, '#ee681f'),
        (100.1, '#da4541'),
        (vmax, '#8c233a'),
    ]
    cmap = LinearSegmentedColormap.from_list(
        'EE347_loading', [(x / vmax, col) for x, col in steps], N=512
    )

    fig, ax = plt.subplots(figsize=(16, 15), constrained_layout=False)
    fig.patch.set_facecolor('white')
    img = ax.imshow(
        loading_pct, origin='upper', aspect='auto', interpolation='bilinear',
        cmap=cmap, norm=Normalize(vmin=0, vmax=vmax),
        extent=(TORQUE_MIN_NM, TORQUE_MAX_NM, 63.5, -0.5)
    )

    # Mark the two reference loading contours on the smooth map.
    # On a 64-row raster, contouring across adjacent rows is just a visual guide.
    X, Y = np.meshgrid(torques, np.arange(64))
    for level, style, color, weight in [(98, '--', '#2e3234', 1.25), (100, '-', '#1d1d1d', 1.6)]:
        try:
            ax.contour(X, Y, loading_pct, levels=[level], colors=[color],
                       linestyles=[style], linewidths=weight)
        except ValueError:
            pass

    # Label each of the 64 rows with actual selected hardware steps, not binary IDs.
    labels = [
        f'R {subset_label(r, RESISTANCES_OHM):<14}  |  C {subset_label(c, CAPACITANCES_UF)}'
        for r, c, _, _ in configurations
    ]
    ax.set_yticks(range(64))
    ax.set_yticklabels(labels, fontsize=6.8, family='monospace')
    for group in range(1, 8):
        ax.axhline(group * 8 - 0.5, color='#f4f4f4', lw=1.8, alpha=0.95)

    ax.set_xlabel('Dynamometer torque (N·m), at fixed 1,770 RPM', fontsize=12, labelpad=10)
    ax.set_ylabel('Feeder 1: enabled resistor steps (Ω) and capacitor steps (µF)', fontsize=11, labelpad=10)
    fig.suptitle('EE 347  |  Transformer loading across 64 load-bank configurations',
                 fontsize=17, weight='bold', y=0.982)
    ax.set_xticks(np.arange(0, TORQUE_MAX_NM + 0.001, 0.125))
    ax.tick_params(axis='x', labelsize=9)
    ax.tick_params(axis='y', length=0, pad=5)

    # Caption makes physical assumptions and rating warnings explicit.
    fig.text(0.50, 0.954,
             '750 VA bank  •  208 V three-phase  •  PF = 0.95 lagging at VFD input  •  ideal efficiencies',
             ha='center', va='center', fontsize=11, color='#424b51')
    fig.text(0.50, 0.928,
             'Green: within rating     |     Yellow/orange: approaching 98–100%     |     Red: >100% overload',
             ha='center', va='center', fontsize=10, color='#424b51')

    cbar = fig.colorbar(img, ax=ax, fraction=0.023, pad=0.02)
    cbar.set_label('Transformer loading (% of 750 VA)', fontsize=11)
    cbar.ax.tick_params(labelsize=9)
    for mark in (98, 100):
        cbar.ax.axhline(mark, color='black', lw=1.3, linestyle='--' if mark == 98 else '-')

    # A torque sweep can exceed the 175-W motor rating even if transformer remains within rating.
    motor_torque_limit = MOTOR_RATED_OUTPUT_W * 60 / (2 * math.pi * RPM)
    if TORQUE_MIN_NM < motor_torque_limit < TORQUE_MAX_NM:
        ax.axvline(motor_torque_limit, color='white', lw=1.2, linestyle=':', alpha=0.9)
        ax.text(motor_torque_limit + 0.005, -1.25, '175 W motor rated shaft limit',
                color='#39424b', fontsize=8, rotation=0, ha='left', va='bottom')

    fig.text(0.5, 0.016,
             'THEORETICAL ONLY: VFD input PF is assumed (not derived from 4.7% power loss); '
             'harmonics, standby draw and actual VFD efficiency excluded.',
             ha='center', fontsize=8.5, color='#555d65')
    plt.subplots_adjust(left=0.30, right=0.90, bottom=0.075, top=0.899)
    fig.savefig(PNG_FILE, dpi=180, facecolor='white')
    plt.close(fig)

    # Export only overloads; record an overload interval rather than hundreds of
    # near-identical rows from the continuous sweep.
    # Each interval is a numerical approximation at TORQUE_SAMPLES resolution.
    interval_count = 0
    with CSV_FILE.open('w', newline='', encoding='utf-8-sig') as fp:
        wr = csv.writer(fp)
        wr.writerow(['Resistors ON (ohm)', 'Capacitors ON (uF)',
                     'First overload torque (N m)', 'First overload motor shaft W',
                     'First overload loading (%)', 'Maximum loading in sweep (%)',
                     'Maximum apparent power (VA)', 'Max line current (A)'])
        for i, (r_flags, c_flags, p_r, q_c) in enumerate(configurations):
            over = np.flatnonzero(loading_pct[i, :] > 100 + 1e-10)
            if len(over) == 0:
                continue
            # Some theoretical configurations can overload at low torque but
            # recover as lagging Q offsets capacitive Q. Handle each run.
            starts = over[np.r_[True, np.diff(over) > 1]]
            ends = over[np.r_[np.diff(over) > 1, True]]
            for start, end in zip(starts, ends):
                j = int(start)
                interval_count += 1
                wr.writerow([
                    subset_label(r_flags, RESISTANCES_OHM),
                    subset_label(c_flags, CAPACITANCES_UF),
                    f'{torques[j]:.4f}', f'{shaft_w[j]:.2f}',
                    f'{loading_pct[i, j]:.2f}',
                    f'{np.max(loading_pct[i, start:end+1]):.2f}',
                    f'{np.max(apparent_va[i, start:end+1]):.2f}',
                    f'{np.max(current_a[i, start:end+1]):.3f}',
                ])

    print(f'Heatmap: {PNG_FILE}')
    print(f'Overload-only CSV: {CSV_FILE} ({interval_count} intervals)')
    print(f'Number of R/C configurations: {len(configurations)}')
    print(f'Torque samples: {len(torques)}')
    print(f'Transformer rated current: {TRANSFORMER_VA/(math.sqrt(3)*V_LL):.3f} A')
    print(f'Sweep maximum: {loading_pct.max():.2f}%')
    print(f'Configurations with any overload: {np.any(loading_pct > 100, axis=1).sum()}')
    print(f'Rated 175-W motor torque at {RPM:g} RPM: {motor_torque_limit:.3f} N*m')


if __name__ == '__main__':
    make_heatmap()
