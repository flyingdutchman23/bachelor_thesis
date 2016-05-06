#to plot
import matplotlib.pyplot as plt
#to plot with numpy arrays
import numpy as np
#to have access to the global constants and variables
from config import ROWS, COLS, GEN_NUMBER, POP_SIZE, MAX_DIST, REAL_DIST_CELL
#for saving a file with time stamp
import time

###helper module to plot specific states and results

def avg_min_max(logbook):
    gen = logbook.select("gen")
    fit_mins = logbook.select("min")
    fit_maxs = logbook.select("max")
    fit_avgs = logbook.select("avg")

    fig, ax1 = plt.subplots()
    #print("gen",gen)
    #print("fit_mins",fit_mins)
    line1 = ax1.plot(gen, fit_mins, "b", label="Minimum Fitness")
    line2 = ax1.plot(gen, fit_maxs, "g", label="Maximum Fitness")
    line3 = ax1.plot(gen, fit_avgs, "r", label="Average Fitness")
    ax1.set_xlabel("Generation")
    ax1.set_ylabel("Fitness")
    # for tl in ax1.get_yticklabels():
        # tl.set_color("b")

    lns = line1 + line2 + line3
    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc="center right")

    plt.show()

def map(data,name):
    values = np.reshape(data,(ROWS,COLS))
    plt.imshow(values, vmin=0, vmax=max(data), interpolation="nearest",
            cmap=plt.get_cmap("gnuplot2"), origin="lower")
    cb = plt.colorbar()
    plt.ylabel("y [m]")
    plt.xlabel("x [m]")
    cb.set_label(name)
    #TODO save plot
    #plt.savefig(savename)

    #show the plot
    plt.show()

def scatter_map_dist(individual):
    """prints the nodes on a white background on a 2d axes. Shows the plot.

    :individual: should be the individual, may work for other kind of data as well

    """
    print(individual)
    fig = plt.figure('Scatter Plot 2')
    # fig, ax = plt.subplots(1, 1)

    rows = []
    cols = []

    values = np.reshape(individual,(ROWS,COLS))
    # print(values)
    for index, gen in np.ndenumerate(values):
        if gen == 0:
            rows.append(index[0] * REAL_DIST_CELL)
            cols.append(index[1] * REAL_DIST_CELL)
            circle = plt.Circle((index[0]*REAL_DIST_CELL,index[1]*REAL_DIST_CELL), 
                    radius=MAX_DIST, color='r',fill=False)
            fig.gca().add_artist(circle)
            fig.gca().plot(index[0]*REAL_DIST_CELL,index[1]*REAL_DIST_CELL)

    fig.gca().scatter(rows,cols)
    name = "nodes_with_circles" + str(int(time.time()))
    fig.savefig(name)
    print("after show")

def nodes_radius(data,individual,name):

    #to have an array with just 0 and 1
    for i, d in enumerate(data):
        if d != 0:
            data[i] = 1
    data = np.add(data,individual)
    map_plot(data,name)
    return None
