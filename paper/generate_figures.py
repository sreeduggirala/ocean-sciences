"""
Generate publication-quality figures for the Stommel 1961 paper.
Figures are saved to paper/ directory as PNG files.
"""
import sys
sys.path.insert(0, '/Users/sree/Python/ocean-sciences/backend')

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from model import StommelModel
from solver import run_simulation, compute_bifurcation, YEARS_TO_SECONDS, V_BOX

# Use a publication-quality style
plt.style.use('seaborn-v0_8-darkgrid')
colors = {
    'q_line': '#1f77b4',
    'se_line': '#ff7f0e',
    'sp_line': '#2ca02c',
    'forward': '#1f77b4',
    'backward': '#ff7f0e',
    'unstable': '#cccccc',
    'tipping': '#d62728',
    'hysteresis': '#ffbb78',
}

def figure_1_schematic():
    """Figure 1: Schematic of two-box model."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # Equatorial box (left, warm/salty)
    eq_box = FancyBboxPatch((0.5, 2), 2.5, 2.5,
                            boxstyle="round,pad=0.1",
                            edgecolor='black', facecolor='#ffe6e6', linewidth=2)
    ax.add_patch(eq_box)
    ax.text(1.75, 3.25, 'Equatorial\nBox', ha='center', va='center', fontsize=11, fontweight='bold')
    ax.text(1.75, 2.3, '$T_e = 25°C$\n$S_e$', ha='center', va='center', fontsize=10)

    # Polar box (right, cold/fresh)
    polar_box = FancyBboxPatch((6.5, 2), 2.5, 2.5,
                              boxstyle="round,pad=0.1",
                              edgecolor='black', facecolor='#e6f0ff', linewidth=2)
    ax.add_patch(polar_box)
    ax.text(7.75, 3.25, 'Polar\nBox', ha='center', va='center', fontsize=11, fontweight='bold')
    ax.text(7.75, 2.3, '$T_p = 5°C$\n$S_p$', ha='center', va='center', fontsize=10)

    # Surface flow (northward, blue if q > 0)
    arrow_surface = FancyArrowPatch((3.2, 4.2), (6.3, 4.2),
                                  arrowstyle='->', mutation_scale=30,
                                  linewidth=2.5, color='#ff6b6b')
    ax.add_patch(arrow_surface)
    ax.text(4.75, 4.6, 'Warm surface flow (q)', ha='center', fontsize=10, color='#ff6b6b', fontweight='bold')

    # Deep return flow (southward)
    arrow_return = FancyArrowPatch((6.3, 1.8), (3.2, 1.8),
                                 arrowstyle='->', mutation_scale=30,
                                 linewidth=2.5, color='#4dabf7')
    ax.add_patch(arrow_return)
    ax.text(4.75, 1.3, 'Cold deep return', ha='center', fontsize=10, color='#4dabf7', fontweight='bold')

    # Freshwater forcing
    ax.annotate('', xy=(1.75, 2), xytext=(1.75, 0.8),
               arrowprops=dict(arrowstyle='->', lw=2, color='#95e1d3'))
    ax.text(1.75, 0.3, 'Freshwater\nforcing $F$', ha='center', fontsize=10,
            color='#95e1d3', fontweight='bold')

    # Equations
    eq_text = r'$q = k[\alpha(T_e - T_p) - \beta(S_e - S_p)]$'
    ax.text(5, 0.3, eq_text, ha='center', fontsize=11,
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    fig.tight_layout()
    fig.savefig('/Users/sree/Python/ocean-sciences/paper/fig1_schematic.png',
               dpi=300, bbox_inches='tight')
    print("✓ Figure 1 saved: fig1_schematic.png")
    plt.close()


def figure_2_timeseries_normal():
    """Figure 2: Time series for normal AMOC preset."""
    model = StommelModel(
        T_e=25, T_p=5, S_e0=36, S_p0=34,
        alpha=1.5e-4, beta=8e-4, k=1.5e-6,
        F=8e-5, t_max=3000, noise_amplitude=0
    )
    result = run_simulation(model, 36, 34, t_max=3000, dt=1)

    fig, ax = plt.subplots(figsize=(11, 6))
    ax2 = ax.twinx()

    # Plot q on left axis
    line1 = ax.plot(result['time'], result['q_sv'],
                    color=colors['q_line'], linewidth=2.2, label='AMOC strength (q)')
    ax.axhline(y=0, color='#ff6b6b', linestyle='--', linewidth=1.5, label='Collapse (q=0)', alpha=0.7)
    ax.axhline(y=15, color='#8b949e', linestyle='--', linewidth=1.5, label='Present-day (~15 Sv)', alpha=0.7)

    # Plot salinities on right axis
    line2 = ax2.plot(result['time'], result['S_e'],
                    color=colors['se_line'], linewidth=2, label='$S_e$ (Eq. salinity)', alpha=0.8)
    line3 = ax2.plot(result['time'], result['S_p'],
                    color=colors['sp_line'], linewidth=2, label='$S_p$ (Polar salinity)', alpha=0.8)

    ax.set_xlabel('Time (years)', fontsize=12, fontweight='bold')
    ax.set_ylabel('AMOC Strength (Sv)', fontsize=12, fontweight='bold', color=colors['q_line'])
    ax2.set_ylabel('Salinity (psu)', fontsize=12, fontweight='bold')
    ax.tick_params(axis='y', labelcolor=colors['q_line'])

    ax.set_xlim(0, 3000)
    ax.grid(True, alpha=0.3)

    # Combine legends
    lines = line1 + line2 + line3
    labels = [l.get_label() for l in lines]
    ax.legend(lines, labels, loc='right', fontsize=10, framealpha=0.95)

    fig.suptitle('Time Series Evolution: Normal AMOC Regime (F = 8×10⁻⁵ psu/s)',
                fontsize=13, fontweight='bold', y=0.98)
    fig.tight_layout()
    fig.savefig('/Users/sree/Python/ocean-sciences/paper/fig2_timeseries_normal.png',
               dpi=300, bbox_inches='tight')
    print("✓ Figure 2 saved: fig2_timeseries_normal.png")
    plt.close()


def figure_3_phase_space():
    """Figure 3: Phase space portrait with nullcline."""
    model = StommelModel(
        T_e=25, T_p=5, S_e0=36, S_p0=34,
        alpha=1.5e-4, beta=8e-4, k=1.5e-6,
        F=8e-5, t_max=3000, noise_amplitude=0
    )
    result = run_simulation(model, 36, 34, t_max=3000, dt=10)

    fig, ax = plt.subplots(figsize=(10, 7))

    # Compute phase space data
    delta_S = result['S_e'] - result['S_p']
    q_sv = result['q_sv']

    # Plot trajectory colored by time
    sc = ax.scatter(delta_S[:-1], q_sv[:-1], c=np.arange(len(delta_S)-1),
                   cmap='viridis', s=30, alpha=0.6, edgecolors='none', label='Trajectory')

    # Plot initial and final states
    ax.plot(delta_S[0], q_sv[0], 'r*', markersize=20, label='Initial state', zorder=5)
    ax.plot(delta_S[-1], q_sv[-1], 'go', markersize=10, label='Final state', zorder=5)

    # Compute and plot nullcline: q = k[α·ΔT − β·ΔS]
    delta_S_range = np.linspace(delta_S.min() - 0.5, delta_S.max() + 0.5, 200)
    q_nullcline = (model.k * (model.alpha * (model.T_e - model.T_p) - model.beta * delta_S_range)) * V_BOX / 1e6
    ax.plot(delta_S_range, q_nullcline, '--', color='#8b949e', linewidth=2.2,
           label='q-nullcline (dq/dt=0)', zorder=3)

    ax.axhline(y=0, color='#ff6b6b', linestyle='-', linewidth=1, alpha=0.5)
    ax.set_xlabel('Salinity Difference $\Delta S = S_e - S_p$ (psu)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Circulation Strength (Sv)', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10, loc='upper right', framealpha=0.95)

    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label('Time (integration steps)', fontsize=11)

    fig.suptitle('Phase Space Portrait: Trajectory Convergence to Attractor',
                fontsize=13, fontweight='bold', y=0.98)
    fig.tight_layout()
    fig.savefig('/Users/sree/Python/ocean-sciences/paper/fig3_phase_space.png',
               dpi=300, bbox_inches='tight')
    print("✓ Figure 3 saved: fig3_phase_space.png")
    plt.close()


def figure_4_bifurcation():
    """Figure 4: Bifurcation diagram with hysteresis."""
    print("  Computing bifurcation diagram (this may take ~30 seconds)...")
    model = StommelModel(
        T_e=25, T_p=5, S_e0=36, S_p0=34,
        alpha=1.5e-4, beta=8e-4, k=1.5e-6,
        F=1e-4, t_max=3000, noise_amplitude=0
    )

    bifurcation_result = compute_bifurcation(
        model, F_min=0, F_max=5e-4, n_points=200
    )

    fig, ax = plt.subplots(figsize=(12, 7))

    # Extract forward and backward branches
    F_values = np.array(bifurcation_result['F_values'])
    q_forward_raw = np.array(bifurcation_result['q_forward'])
    q_backward_raw = np.array(bifurcation_result['q_backward'])

    # Convert from 1/s to Sv (q is already in 1/s, need to convert)
    q_forward = q_forward_raw * V_BOX / 1e6
    q_backward = q_backward_raw * V_BOX / 1e6

    # Find tipping points
    tipping_points = bifurcation_result.get('tipping_points', [])
    tp_f = [tp['F'] for tp in tipping_points]
    tp_q = [tp['q'] * V_BOX / 1e6 for tp in tipping_points]

    # Plot forward and backward branches
    ax.plot(F_values * 1e4, q_forward, '-o', color=colors['forward'],
           linewidth=2.2, markersize=4, label='Forward sweep (stable upper)', alpha=0.8)
    ax.plot(F_values * 1e4, q_backward, '-s', color=colors['backward'],
           linewidth=2.2, markersize=4, label='Backward sweep (stable lower)', alpha=0.8)

    # Shade hysteresis region if tipping points exist
    if len(tipping_points) >= 2:
        F_tipping = sorted([tp['F'] for tp in tipping_points])
        ax.axvspan(F_tipping[0] * 1e4, F_tipping[-1] * 1e4,
                  alpha=0.15, color=colors['hysteresis'], label='Hysteresis window')

    # Plot tipping points
    if tp_f:
        ax.plot(np.array(tp_f) * 1e4, tp_q, 'D', color=colors['tipping'],
               markersize=10, label='Tipping points', zorder=5)

    # Reference lines
    ax.axhline(y=15, color='#8b949e', linestyle='--', linewidth=1.5, alpha=0.6, label='Present-day AMOC')
    ax.axhline(y=5, color='#8b949e', linestyle=':', linewidth=1.5, alpha=0.6, label='Weakened state')
    ax.axhline(y=0, color='#ff6b6b', linestyle='-', linewidth=1.5, alpha=0.7, label='Collapse')

    # Current F position
    ax.axvline(x=1e-4 * 1e4, color='#95e1d3', linestyle='-.', linewidth=1.5, alpha=0.7,
              label='Default F')

    ax.set_xlabel('Freshwater Flux F (×10⁻⁴ psu/s)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Steady-State AMOC Strength (Sv)', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10, loc='best', framealpha=0.95)
    ax.set_xlim(-0.1, 5.5)

    fig.suptitle('Bifurcation Diagram: AMOC Hysteresis and Tipping Points',
                fontsize=13, fontweight='bold', y=0.98)
    fig.tight_layout()
    fig.savefig('/Users/sree/Python/ocean-sciences/paper/fig4_bifurcation.png',
               dpi=300, bbox_inches='tight')
    print("✓ Figure 4 saved: fig4_bifurcation.png")
    plt.close()


def figure_5_normal_vs_collapsed():
    """Figure 5: Comparison of normal vs collapsed AMOC."""
    # Normal AMOC
    model_normal = StommelModel(
        F=8e-5, t_max=3000, S_e0=36, S_p0=34
    )
    result_normal = run_simulation(model_normal, 36, 34, t_max=3000, dt=5)

    # Collapsed AMOC
    model_collapsed = StommelModel(
        F=3e-4, t_max=3000, S_e0=36, S_p0=34.5
    )
    result_collapsed = run_simulation(model_collapsed, 36, 34.5, t_max=3000, dt=5)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Normal AMOC
    ax1_twin = ax1.twinx()
    ax1.plot(result_normal['time'], result_normal['q_sv'],
            color=colors['q_line'], linewidth=2.2)
    ax1.axhline(y=0, color='#ff6b6b', linestyle='--', linewidth=1, alpha=0.7)
    ax1.axhline(y=15, color='#8b949e', linestyle='--', linewidth=1, alpha=0.7)
    ax1_twin.plot(result_normal['time'], result_normal['S_e'],
                 color=colors['se_line'], linewidth=1.8, alpha=0.7)
    ax1_twin.plot(result_normal['time'], result_normal['S_p'],
                 color=colors['sp_line'], linewidth=1.8, alpha=0.7)

    ax1.set_ylabel('AMOC (Sv)', fontsize=11, fontweight='bold', color=colors['q_line'])
    ax1_twin.set_ylabel('Salinity (psu)', fontsize=11, fontweight='bold')
    ax1.set_xlabel('Time (years)', fontsize=11, fontweight='bold')
    ax1.set_title('Normal AMOC\n(F = 8×10⁻⁵ psu/s, q ≈ 15 Sv)', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='y', labelcolor=colors['q_line'])

    # Collapsed AMOC
    ax2_twin = ax2.twinx()
    ax2.plot(result_collapsed['time'], result_collapsed['q_sv'],
            color=colors['q_line'], linewidth=2.2)
    ax2.axhline(y=0, color='#ff6b6b', linestyle='--', linewidth=1, alpha=0.7)
    ax2_twin.plot(result_collapsed['time'], result_collapsed['S_e'],
                 color=colors['se_line'], linewidth=1.8, alpha=0.7)
    ax2_twin.plot(result_collapsed['time'], result_collapsed['S_p'],
                 color=colors['sp_line'], linewidth=1.8, alpha=0.7)

    ax2.set_ylabel('AMOC (Sv)', fontsize=11, fontweight='bold', color=colors['q_line'])
    ax2_twin.set_ylabel('Salinity (psu)', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Time (years)', fontsize=11, fontweight='bold')
    ax2.set_title('Collapsed AMOC\n(F = 3×10⁻⁴ psu/s, q ≈ 0 Sv)', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='y', labelcolor=colors['q_line'])

    fig.suptitle('Stable States: Thermally-Driven vs Collapsed AMOC',
                fontsize=13, fontweight='bold', y=1.00)
    fig.tight_layout()
    fig.savefig('/Users/sree/Python/ocean-sciences/paper/fig5_comparison.png',
               dpi=300, bbox_inches='tight')
    print("✓ Figure 5 saved: fig5_comparison.png")
    plt.close()


def figure_6_amoc_calibration():
    """Figure 6: Model vs observed AMOC."""
    # Simulate model at default parameters
    model = StommelModel(F=8e-5)
    result = run_simulation(model, 36, 34, t_max=3000, dt=1)
    q_model = result['q_sv'][-1]  # Final value

    # RAPID array mean
    q_rapid = 16.9  # Sv, 2004-2020 mean

    fig, ax = plt.subplots(figsize=(9, 6))

    bars = ax.bar(['Stommel Model\n(Normal AMOC)', 'RAPID Array\n(2004-2020 mean)'],
                  [q_model, q_rapid],
                  color=['#58a6ff', '#4dabf7'],
                  edgecolor='black',
                  linewidth=2,
                  width=0.5,
                  alpha=0.85)

    ax.axhline(y=0, color='#ff6b6b', linestyle='-', linewidth=2)
    ax.set_ylabel('Circulation Strength (Sv)', fontsize=12, fontweight='bold')
    ax.set_ylim(0, 20)
    ax.grid(True, axis='y', alpha=0.3)

    # Add value labels on bars
    for i, (bar, val) in enumerate(zip(bars, [q_model, q_rapid])):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.3,
               f'{val:.1f} Sv',
               ha='center', va='bottom', fontsize=11, fontweight='bold')

    fig.suptitle('Model Calibration: Stommel vs Observed AMOC',
                fontsize=13, fontweight='bold', y=0.98)

    # Add text box with educational content
    textstr = ('The Stommel (1961) two-box model captures the essential physics of AMOC\n'
              'tipping points. Default parameters yield ~15 Sv, consistent with\n'
              'observational estimates from the RAPID array monitoring project.')
    ax.text(0.5, 0.35, textstr, transform=ax.transAxes,
           fontsize=10, verticalalignment='top', horizontalalignment='center',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))

    fig.tight_layout()
    fig.savefig('/Users/sree/Python/ocean-sciences/paper/fig6_calibration.png',
               dpi=300, bbox_inches='tight')
    print("✓ Figure 6 saved: fig6_calibration.png")
    plt.close()


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Generating publication-quality figures for Stommel paper")
    print("="*60 + "\n")

    figure_1_schematic()
    figure_2_timeseries_normal()
    figure_3_phase_space()
    figure_4_bifurcation()
    figure_5_normal_vs_collapsed()
    figure_6_amoc_calibration()

    print("\n" + "="*60)
    print("All figures generated successfully!")
    print("Location: /Users/sree/Python/ocean-sciences/paper/")
    print("="*60 + "\n")
