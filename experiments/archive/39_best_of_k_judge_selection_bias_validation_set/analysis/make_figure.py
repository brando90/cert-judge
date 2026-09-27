#!/usr/bin/env python3
"""Figure for experiment 39 from its committed CSV outputs (no Monte Carlo is rerun).

Writes figures/best_of_k_selection_bias.{pdf,png}. Colors follow the reference categorical
order (blue, orange, aqua; validated with the dataviz palette checker); model curves are
gray and dashed so the measured curves carry the emphasis.

Run: python3 experiments/39_best_of_k_judge_selection_bias_validation_set/analysis/make_figure.py
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

EXP = Path(__file__).resolve().parents[1]
RESULTS = EXP / 'results'
FIGURES = EXP / 'figures'

BLUE, ORANGE, AQUA = '#2a78d6', '#eb6834', '#1baf7a'
INK, INK2, MUTED = '#0b0b0b', '#52514e', '#898781'
GRID, AXIS = '#e1e0d9', '#c3c2b7'
VIEW = 'avg'


def rows(name):
    with (RESULTS / name).open() as stream:
        return list(csv.DictReader(stream))


def series(data, x='K', y='mean', **match):
    picked = [r for r in data if all(r[k] == v for k, v in match.items())]
    picked.sort(key=lambda r: int(r[x]))
    return [int(r[x]) for r in picked], [float(r[y]) for r in picked]


def style(ax, title, ylabel):
    ax.set_xscale('log', base=2)
    ax.set_xticks([1, 2, 4, 8, 16, 32, 64, 109])
    ax.set_xticklabels(['1', '2', '4', '8', '16', '32', '64', '109'])
    ax.minorticks_off()
    ax.set_xlim(0.85, 135)
    ax.set_xlabel('Configurations compared (K)', fontsize=8, color=INK2)
    ax.set_ylabel(ylabel, fontsize=8, color=INK2)
    ax.set_title(title, fontsize=8, color=INK)
    ax.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('left', 'bottom'):
        ax.spines[side].set_color(AXIS)
    ax.tick_params(labelsize=7, colors=INK2, length=2.5)
    ax.get_xticklabels()[-1].set_horizontalalignment('left')   # 109 sits less than an octave after 64


def main():
    a, b, c = rows('A_null_best_of_k.csv'), rows('B_split_half_selection.csv'), rows('C_synthetic_best_of_k.csv')
    fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.75))
    line = dict(linewidth=1.6, markersize=3.6)

    # (a) Null: the winner's apparent agreement when no configuration tracks the labels.
    ax = axes[0]
    k, mean = series(a, view=VIEW)
    _, p95 = series(a, y='p95', view=VIEW)
    ax.plot(k, mean, color=BLUE, marker='o', label='109 recorded configurations, mean', **line)
    ax.plot(k, p95, color=BLUE, linewidth=0.9, alpha=0.55, label='Same, 95th percentile')
    for setting, shade, label in (('null-indep', INK2, 'Model, independent judges'),
                                  ('null-shared', MUTED, 'Model, shared judge noise')):
        ks, ys = series(c, y='mean_inflation', label_model='extended', setting=setting, n_items='72')
        ax.plot(ks, ys, color=shade, linestyle=(0, (4, 2)), marker='s', label=label, **line)
    ax.axhline(0, color=AXIS, linewidth=0.8)
    ax.set_ylim(-0.03, 0.57)
    style(ax, '(a) Permuted labels: no signal', "Winner's Spearman (permuted labels)")
    ax.legend(fontsize=6.3, frameon=False, loc='upper left', handlelength=2.2)

    # (b) Split halves: agreement on the choosing half and on held-out problems.
    ax = axes[1]
    ks, sel = series(b, y='mean_selection_rho', view=VIEW, rule='label')
    _, held = series(b, y='mean_heldout_rho', view=VIEW, rule='label')
    ax.plot(ks, sel, color=BLUE, marker='o', markerfacecolor='white', label='By labels, choosing half', **line)
    ax.plot(ks, held, color=BLUE, marker='o', label='By labels, held-out half', **line)
    for rule, color, marker, label in (('property', ORANGE, 's', 'By v1 index, held-out half'),
                                       ('random', AQUA, '^', 'At random, held-out half')):
        ks, ys = series(b, y='mean_heldout_rho', view=VIEW, rule=rule)
        ax.plot(ks, ys, color=color, marker=marker, label=label, **line)
    ax.set_ylim(-0.02, 0.66)
    style(ax, '(b) Choose on half the problems', 'Spearman with averaged labels')
    ax.legend(fontsize=6, frameon=False, loc='lower right', handlelength=2.2, borderaxespad=0.2, labelspacing=0.3)

    # (c) Overstatement: measured at 36 items, modelled at 36 and 72 items.
    ax = axes[2]
    ks, ys = series(b, y='mean_optimism', view=VIEW, rule='label')
    ax.plot(ks, ys, color=BLUE, marker='o', label='Measured, 36-item halves', **line)
    for n_items, shade, label in (('36', MUTED, 'Model, 36 items'), ('72', INK2, 'Model, all 72 items')):
        kk, yy = series(c, y='mean_inflation', label_model='extended', setting='weak-hetero', n_items=n_items)
        ax.plot(kk, yy, color=shade, linestyle=(0, (4, 2)), marker='s', label=label, **line)
    ax.axhline(0, color=AXIS, linewidth=0.8)
    ax.set_ylim(-0.03, 0.43)
    style(ax, "(c) Overstatement of the winner", 'Chosen minus held-out Spearman')
    ax.legend(fontsize=6.3, frameon=False, loc='upper left', handlelength=2.2)

    fig.tight_layout(w_pad=1.2)
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / 'best_of_k_selection_bias.pdf', metadata={'CreationDate': None, 'ModDate': None})
    fig.savefig(FIGURES / 'best_of_k_selection_bias.png', dpi=220)
    plt.close(fig)
    print('wrote', FIGURES / 'best_of_k_selection_bias.pdf')


if __name__ == '__main__':
    main()
