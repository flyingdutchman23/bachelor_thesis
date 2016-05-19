#to plot
import matplotlib.pyplot as plt
#to plot with numpy arrays
import numpy as np
#to have access to the global constants and variables
from config import ROWS, COLS, GEN_NUMBER, POP_SIZE, MAX_DIST, REAL_DIST_CELL, IND_LEN
#for saving a file with time stamp
import time
#to plot map of received packets
import spne
#to use a Graph to compute the SPNE fitness, to simulate Multi-Hop
import graph_tool.all as gt

import init_functions as init

import my_util

#so every saved plot in 1 run has same time
START_TIME = time.time()
START_TIME_STR = str(int(START_TIME))

###helper module to plot specific states and results

def draw_individual_graph(individual,name):

    MAX_WINDOW = 1000
    output_size = (80 * COLS, 80 * ROWS)

    #to keep the relation of the window and to keep the size smaller than MAX_WINDOW
    if max(output_size) > MAX_WINDOW:
        if ROWS > COLS:
            col_size = int(output_size[1] / (output_size[0] / MAX_WINDOW))
            output_size = (MAX_WINDOW,col_size)
        elif COLS > ROWS:
            row_size = int(output_size[0] / (output_size[1] / MAX_WINDOW))
            output_size = (row_size,MAX_WINDOW)
        else:
            output_size = (MAX_WINDOW,MAX_WINDOW)

    #build Graph to store nodes for plotting
    nodes = np.nonzero(individual)[0]
    g = spne.build_graph(nodes)

    positions = g.new_vertex_property("vector<double>")
    for node_index in range(len(nodes)):
        pos = my_util.onedpos_to_2dpos(nodes[node_index]) 
        pos =  (pos[1] * output_size[0] / COLS,
                pos[0] * output_size[1] / ROWS)
        positions[g.vertex(node_index)] = pos


    name += "_" + START_TIME_STR + ".png"
    gt.graph_draw(g, positions, vertex_text=g.vertex_index, vertex_font_size=18, 
            output=name, output_size=output_size)


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

def map(data,name,save=True,to_show=True,description=""):
    #clear last figure, if it exists
    plt.clf()
    values = np.reshape(data,(ROWS,COLS))

    plt.gcf().add_axes((0.2,0.2,0.7,0.7))
    plt.imshow(values, vmin=0, vmax=max(data), interpolation="nearest",
            cmap=plt.get_cmap("gray"), origin="lower")
    cb = plt.colorbar()
    plt.ylabel("y [m]")
    plt.xlabel("x [m]")
    plt.gcf().gca().set_ylim([-0.5,ROWS-0.5])
    plt.gcf().gca().set_xlim([-0.5,COLS-0.5])
    plt.gcf().suptitle(name)
    cb.set_label(name)
    plt.figtext(0.1,0.1,description)

    #save the plot
    if save:
        name = name + "_" + START_TIME_STR
        plt.savefig(name)

    #show the plot
    if to_show:
        plt.show()

def scatter_map_dist(individual,name,save=True,to_show=True,print_fitness=True,
        description=""):
    """prints the nodes on a white background on a 2d axes. Shows the plot.

    :individual: should be the individual, may work for other kind of data as well

    """
    fig = plt.figure(figsize=(8,8))

    #make correct relation of width and height in plot
    left = 0.2
    bottom = 0.2
    if ROWS > COLS:
        left += (0.9 - left) * (1 - COLS / ROWS)
    elif COLS > ROWS:
        bottom += (0.9 - bottom) * (1 - ROWS / COLS)

    print("left, bottom: ",left,bottom)
    fig.add_axes((left,bottom, 0.9 - left, 0.9 - bottom))

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
    fig.gca().set_ylim([-0.5,ROWS-0.5])
    fig.gca().set_xlim([-0.5,COLS-0.5])
    fig.suptitle(name)

    #add description
    if print_fitness:
        description += "Fitness: " + str(individual.fitness.values)
    fig.text(0.1,0.1,description)

    if save:
        name = "nodes_with_circles" + "_" + name + START_TIME_STR
        fig.savefig(name)

    if to_show:
        plt.show()

def nodes_with_range(individual,name,save=True,to_show=True):

    data, nodes = spne.received_packets(individual)
    name += ", nodes: " + str(nodes) + ", packs: " + str(sum(data))
    map(data,name,save,to_show)

def graph_nodes_with_range(individual,name,save=True,to_show=True, print_fitness=True):

    #array to store received packets
    data = init.zeros()
    nodes = np.nonzero(individual)[0]
    #build the Graph to store the nodes
    g = spne.build_graph(nodes)

    #add probe node to graph
    probe_node = g.add_vertex()
    # probe node iterates over grid. Probe node is added to graph, reachable vertexes are
    # computed and summed up
    for probe in range(IND_LEN):
        for node_index, node in enumerate(nodes):
            if spne.packet_received(probe, node) == True:
                g.add_edge(probe_node,g.vertex(node_index))
        labeling = gt.label_out_component(g,probe_node)
        #if the nodes are connected
        # then increase the field where the probe nodes is currently in the matrix
        data[probe] += sum(labeling.a) - 1
        g.clear_vertex(probe_node)

    name += ", nodes: " + str(len(nodes)) + ", packs: " + str(sum(data))

    description = ""
    if print_fitness:
        description = "Fitness: " + str(individual.fitness.values)
    map(data,name,save,to_show,description)
