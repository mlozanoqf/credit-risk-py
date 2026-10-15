"""Presentation helpers; financial calculations remain in scoring.py and chapter code."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from scipy.stats import gaussian_kde
from sklearn.metrics import roc_curve,roc_auc_score
from shared.output import BLUE,RED,GREEN

COLORS = {'age':'#E69F00','int':'#7A5195','multi':GREEN,'full':BLUE,
          'logi_full':BLUE,'single_tree':GREEN,'xgboost':RED}


def density(ax,p,label,color):
    grid = np.linspace(max(0,np.min(p)-.05),min(1,np.max(p)+.05),512)
    curve = gaussian_kde(p)(grid)
    ax.plot(grid,curve,color=color,label=label)
    ax.fill_between(grid,curve,color=color,alpha=.18)
    ax.xaxis.set_major_formatter(PercentFormatter(1))
    ax.set(xlabel='Predicted default probability',ylabel='Density')
    return grid,curve


def distributions(predictions):
    fig,ax = plt.subplots()
    for name,p in predictions.items(): density(ax,p,name,COLORS[name])
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.19),ncol=len(predictions))
    fig.subplots_adjust(bottom=.23)
    return fig


def boxes(predictions):
    fig,ax = plt.subplots()
    ax.boxplot(list(predictions.values()),tick_labels=list(predictions),showfliers=True,
               flierprops={'markersize':2,'alpha':.2},orientation='horizontal')
    ax.set_xlabel('Predicted default probability')
    ax.xaxis.set_major_formatter(PercentFormatter(1))
    return fig


def roc_plot(y,predictions):
    fig,ax = plt.subplots(figsize=(6,6))
    for name,p in predictions.items():
        fpr,tpr,_ = roc_curve(y,p,drop_intermediate=False)
        ax.plot(1-fpr,tpr,color=COLORS.get(name,BLUE),lw=1.8,
                label=f'{name}: AUC {roc_auc_score(y,p):.4f}')
    ax.plot([1,0],[0,1],color='.5',ls='--',lw=.8)
    ax.set(xlim=(1.02,-.02),ylim=(-.02,1.02),xlabel='Specificity',ylabel='Sensitivity')
    ax.xaxis.set_major_formatter(PercentFormatter(1))
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.14))
    fig.subplots_adjust(bottom=.23)
    return fig


def calibration_plot(frames):
    fig,ax = plt.subplots(figsize=(6,6))
    limit = np.ceil(10*max(max(t.average_predicted_pd.max(),t.observed_default_rate.max())
                         for t in frames.values()))/10
    ax.plot([0,limit],[0,limit],color='.5',ls='--',lw=.8)
    for name,t in frames.items():
        ax.plot(t.average_predicted_pd,t.observed_default_rate,'o-',label=name,color=COLORS[name])
    ax.set(xlim=(0,limit),ylim=(0,limit),xlabel='Mean predicted PD',ylabel='Observed default rate')
    ax.xaxis.set_major_formatter(PercentFormatter(1)); ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.14),ncol=2)
    fig.subplots_adjust(bottom=.23)
    return fig
