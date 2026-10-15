"""Readable two-panel view of the fitted CART; all nodes and leaves are retained."""
import matplotlib.pyplot as plt
from shared.output import BLUE


def tree_figure(model,names):
    tree=model.tree_
    def label(node):
        leaf=tree.children_left[node]==tree.children_right[node]
        pd=tree.value[node,0,1]/tree.value[node,0].sum()
        split='' if leaf else f'{names[tree.feature[node]]} <= {tree.threshold[node]:.3f}\n'
        return f'{"Leaf" if leaf else "Node"} {node}\n{split}n = {tree.n_node_samples[node]:,}\nPD = {pd:.1%}'
    fig,axes=plt.subplots(2,1,figsize=(10,10))
    fig.text(.5,.98,label(0),ha='center',va='top',fontsize=10,
             bbox={'facecolor':'white','edgecolor':BLUE,'pad':5})
    for ax,root,branch in zip(axes,[tree.children_left[0],tree.children_right[0]],['True','False']):
        positions={}
        leaf_x=[]
        def place(node,depth):
            left,right=tree.children_left[node],tree.children_right[node]
            if left==right:
                x=len(leaf_x); leaf_x.append(x)
            else:
                x=(place(left,depth+1)+place(right,depth+1))/2
            positions[node]=(x,-depth)
            return x
        place(root,0)
        for node,(x,y) in positions.items():
            left,right=tree.children_left[node],tree.children_right[node]
            leaf=left==right
            if not leaf:
                for child in [left,right]:
                    xx,yy=positions[child]
                    ax.plot([x,xx],[y,yy],color='.45',lw=.8,zorder=0)
            ax.text(x,y,label(node),ha='center',va='center',fontsize=8.5,
                     bbox={'facecolor':'#e8f2f7' if leaf else 'white',
                           'edgecolor':BLUE,'boxstyle':'square,pad=.3'})
        ax.set_xlim(-.55,len(leaf_x)-.45)
        ax.set_ylim(min(y for x,y in positions.values())-.55,.6)
        ax.set_title(f'{branch} branch from root node 0',fontsize=11,pad=12)
        ax.axis('off')
    fig.subplots_adjust(top=.80,bottom=.03,left=.025,right=.975,hspace=.25)
    return fig
