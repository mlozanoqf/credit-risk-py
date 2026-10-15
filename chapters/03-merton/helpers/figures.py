"""Presentation only: calculations are visible in chapter.qmd and model.py."""
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np


def plot_paths(matrix, debt, colors=None, alpha=0.7, width=0.8):
    fig, ax = plt.subplots(layout='constrained')
    for i in range(matrix.shape[1]):
        color = colors[i] if colors is not None else '#444444'
        ax.plot(np.arange(matrix.shape[0]), matrix[:, i], color=color, alpha=alpha, lw=width)
    ax.axhline(debt, color='#B22222', lw=1.3)
    if matrix.shape[1]:
        ax.scatter([0], [matrix[0, 0]], color='#0072B2', zorder=4)
    else:
        ax.text(0.5, 0.5, 'No paths in this group for this simulation.',
                transform=ax.transAxes, ha='center')
    ax.set(xlabel='Time in days (from 0 to T)', ylabel=r'$V_t$')
    return fig, ax


def sensitivity(x, y, current_x, current_pd, xlabel, limits=None, percent_x=False, decimals=0):
    fig, ax = plt.subplots(layout='constrained')
    ax.plot(x, y, lw=1.8, color='#0072B2')
    ax.axvline(current_x, ls='--', lw=0.7, color='0.3')
    ax.axhline(current_pd, ls='--', lw=0.7, color='0.3')
    ax.scatter([current_x], [current_pd], edgecolor='#B77900', facecolor='white', s=45, zorder=4)
    ax.set(xlabel=xlabel, ylabel='Risk-neutral PD')
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=decimals))
    if limits is not None:
        ax.set_ylim(*limits)
    if percent_x:
        ax.xaxis.set_major_formatter(PercentFormatter(1))
    return fig


def capital_plot(debts, curves, labels, points, initial_pd, initial_debt,
                 xlimits=None, ylimits=None):
    colors = ['#009E73', '#7A5195', 'black', '#0072B2', '#B22222']
    fig, ax = plt.subplots(figsize=(7, 5), layout='constrained')
    for curve, label, color in zip(curves, labels, colors):
        ax.plot(debts, curve, label=label, color=color, lw=1.6)
    for d, p, color in points:
        ax.axvline(d, ls='--', lw=0.65, color='0.3')
        ax.axhline(p, ls='--', lw=0.65, color='0.3')
        ax.scatter([d], [p], facecolor=color, edgecolor='black', s=55, zorder=4)
    ax.set(xlabel=f'Promised debt payment (initial D = {initial_debt:g})',
           ylabel=f'Risk-neutral PD (initial {initial_pd:.2%})')
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    if xlimits:
        ax.set_xlim(*xlimits)
    if ylimits:
        ax.set_ylim(*ylimits)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.17), ncol=3, fontsize=9)
    return fig
