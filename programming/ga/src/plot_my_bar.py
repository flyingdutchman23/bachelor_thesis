#to plot
import matplotlib.pyplot as plt
#to plot with numpy arrays
import numpy as np
# to measure needed time for functions
import time
# to draw buildings
import io
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon

###My package imports
#to have access to the global constants and variables
import config
#to plot map of received packets
import spne
#to use a Graph to compute the SPNE fitness, to simulate Multi-Hop
import graph_tool.all as gt
import init_functions as init
import my_util
import ralans_wrapper as ralans
import ralans_helper
from constants import XAXIS, YAXIS 

###helper module to plot specific states and results

def bar_plot():

    save_folder = '/home/joris/Desktop/'
    name = 'bar_evals_flex'
    # name = 'bar_evals_fix'

    # values = [13000, 13609, 7945.43, 19650]
    values = [12000.0, 20173.0, 36038.0] 
    descs = ['Zufall', 'GA', 'Eröffnung']
    # descs = ['Zufall', 'lokale Suche', 'GA', 'Eröffnung']

    width = 0.25       # the width of the bars
    ind = np.arange(len(values))  # the x locations for the groups
    ind = ind + width/2

    
    fig, ax = plt.subplots()
    rects1 = ax.bar(ind, values, width, color='r')
    
    # add some text for labels, title and axes ticks
    ax.set_ylabel('Anzahl Auswertungen')
    ax.set_xlabel('Suchverfahren')
    # ax.set_title('Scores by group and gender')
    ax.set_xticks(ind + width/2)
    ax.set_xticklabels(descs)
    
    
    autolabel(rects1, ax)
    
    fig.subplots_adjust(top=0.92, bottom=0.12, left=0.12, right=0.95)

    #save the plot
    fig.savefig(save_folder + name + '.eps')
    plt.show()

def autolabel(rects, ax):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                '%.2f' % float(height),
                ha='center', va='bottom')

def main():
    bar_plot()

    
if __name__ == "__main__":
    main()
