#to plot
import matplotlib.pyplot as plt
#to plot with numpy arrays
import numpy as np
#to have access to the global constants and variables
from config import ROWS, COLS, GEN_NUMBER, POP_SIZE, MAX_DIST, REAL_DIST_CELL
#for saving a file with time stamp
import time
#to plot map of received packets
import spne
#to use a Graph to compute the SPNE fitness, to simulate Multi-Hop
import graph_tool.all as gt

#so every saved plot in 1 run has same time
START_TIME = time.time()
START_TIME_STR = str(int(START_TIME))

###helper module to plot specific states and results

def draw_individual_graph(individual,name):

    nodes = np.nonzero(individual)[0]
    #Graph to store nodes
    g = gt.Graph(directed=False)
    #add a vertex for each node in the individual
    num_of_nodes = len(nodes)
    g.add_vertex(num_of_nodes)

    #build Graph by adding an edge between the nodes, which are connected
    for node_index1, node1 in enumerate(nodes):
        for node_index2, node2 in enumerate(nodes):
            if spne.packet_received(node1,node2) == True:
                g.add_edge(g.vertex(node_index1),g.vertex(node_index2))

    name += "_" + START_TIME_STR + ".png"
    gt.graph_draw(g, vertex_text=g.vertex_index, vertex_font_size=18, output=name)


def avg_min_max(logbook,save=False,to_show=True):
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

    #save the plot
    if save:
        name = "Statistics_" + START_TIME_STR
        fig.savefig(name)

    if to_show:
        plt.show()

def map(data,name,save=True,to_show=True):
    #clear last figure, if it exists
    plt.clf()
    values = np.reshape(data,(ROWS,COLS))
    plt.imshow(values, vmin=0, vmax=max(data), interpolation="nearest",
            cmap=plt.get_cmap("gray"), origin="lower")
    cb = plt.colorbar()
    plt.ylabel("y [m]")
    plt.xlabel("x [m]")
    plt.gcf().gca().set_ylim([0,ROWS-0.5])
    plt.gcf().gca().set_xlim([0,COLS-0.5])
    cb.set_label(name)

    #save the plot
    if save:
        name = name + "_" + START_TIME_STR
        plt.savefig(name)

    #show the plot
    if to_show:
        plt.show()

def scatter_map_dist(individual,name,save=True,to_show=True):
    """prints the nodes on a white background on a 2d axes. Shows the plot.

    :individual: should be the individual, may work for other kind of data as well

    """
    fig = plt.figure('Plots ')

    rows = []
    cols = []

    values = np.reshape(individual,(ROWS,COLS))

    for index, gen in np.ndenumerate(values):
        if gen == 1:
            rows.append(index[0] * REAL_DIST_CELL)
            cols.append(index[1] * REAL_DIST_CELL)
            circle = plt.Circle((index[1]*REAL_DIST_CELL,index[0]*REAL_DIST_CELL), 
                    radius=MAX_DIST, color='r',fill=False)
            fig.gca().add_artist(circle)
            fig.gca().plot(index[1]*REAL_DIST_CELL,index[0]*REAL_DIST_CELL)

    fig.gca().scatter(cols,rows)
    fig.gca().set_ylim([0,ROWS-0.5])
    fig.gca().set_xlim([0,COLS-0.5])

    if save:
        name = "nodes_with_circles" + "_" + name + START_TIME_STR
        fig.savefig(name)

    if to_show:
        plt.show()

def nodes_with_range(individual,name,save=True,to_show=True):

    data, nodes = spne.received_packets(individual)
    name += ", nodes: " + str(nodes) + ", packs: " + str(sum(data))
    map(data,name,save,to_show)
