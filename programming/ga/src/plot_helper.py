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

def draw_individual_graph(individual,name):

    MAX_WINDOW = 1000
    output_size = (MAX_WINDOW, MAX_WINDOW)

    #build Graph to store nodes for plotting
    nodes = np.nonzero(individual)[0]
    g = spne.build_graph(nodes)

    positions = g.new_vertex_property("vector<double>")
    for node_index in range(len(nodes)):
        pos = my_util.onedpos_to_2dpos(nodes[node_index], config.POSITIONS) 
        # correct the y value, because the origin(the 0 value) is at the top and in
        # another plot it is at the bottom
        pos[YAXIS] = config.BORDERS[2 + YAXIS] - pos[YAXIS]
        positions[g.vertex(node_index)] = pos


    # store it as a png picture
    name += ".png"

    gt.graph_draw(g, positions, vertex_text=g.vertex_index, vertex_font_size=12, 
            output=config.FOLDER+name, output_size=output_size)

def avg_min_max(logbook,save=True,to_show=True):
    gen = logbook.select("gen")
    fit_mins = logbook.select("min")
    fit_maxs = logbook.select("max")
    fit_avgs = logbook.select("avg")
    fit_hof = logbook.select("hof_max")

    fig, ax1 = plt.subplots()
    #print("gen",gen)
    #print("fit_mins",fit_mins)
    line1 = ax1.plot(gen, fit_mins, "b", label="Minimum Fitness")
    line2 = ax1.plot(gen, fit_maxs, "g", label="Maximum Fitness")
    line3 = ax1.plot(gen, fit_avgs, "r", label="Average Fitness")
    line4 = ax1.plot(gen, fit_hof, "y", label="Hall of Fame")
    ax1.set_xlabel("Generation")
    ax1.set_ylabel("Fitness")
    # for tl in ax1.get_yticklabels():
        # tl.set_color("b")

    lns = line1 + line2 + line3 + line4
    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc="center right")

    #save the plot
    if save:
        name = "Statistics"
        fig.savefig(config.FOLDER+name)

    if to_show:
        plt.show()

def map(data,name,save=True,to_show=True,description=""):
    #clear last figure, if it exists
    plt.clf()
    values = np.reshape(data,(config.LENG[YAXIS],config.LENG[XAXIS]))

    plt.gcf().add_axes((0.2,0.2,0.7,0.7))
    plt.imshow(values, vmin=0, vmax=max(data), interpolation="nearest",
            cmap=plt.get_cmap("gray"), origin="lower")
    cb = plt.colorbar()
    plt.ylabel("y [m]")
    plt.xlabel("x [m]")
    plt.gcf().gca().set_ylim([-0.5,config.LENG[1]-0.5])
    plt.gcf().gca().set_xlim([-0.5,config.LENG[0]-0.5])
    plt.gcf().suptitle(name)
    cb.set_label(name)
    plt.figtext(0.1,0.1,description)

    #save the plot
    if save: 
        plt.savefig(config.FOLDER+name)

    #show the plot
    if to_show:
        plt.show()

def scatter_map_dist(individual, name, save=True, to_show=True, 
        print_fitness=True, description="", add_circles=True, add_grid=False,
        add_buildings=True):
    """prints the nodes on a white background on a 2d axes. Shows the plot.

    :individual: should be the individual, may work for other kind of data as well

    """
    fig = plt.figure(figsize=(8,8))

    #make correct relation of width and height in plot
    left = 0.2
    bottom = 0.2
    size_x = config.BORDERS[2] - config.BORDERS[0] + 1
    size_y = config.BORDERS[3] - config.BORDERS[1] + 1
    if size_y > size_x:
        left += (0.9 - left) * (1 - size_x / size_y)
    elif size_x > size_y:
        bottom += (0.9 - bottom) * (1 - size_y / size_y)
    fig.add_axes((left,bottom, 0.9 - left, 0.9 - bottom))

    x_values = []
    y_values = []

    print('BORDERS:', config.BORDERS)

    for index, gen in enumerate(individual):
        if gen == 1:
            transmitter = config.POSITIONS[index]
            print('transmitter: ', transmitter)
            x_values.append(transmitter[XAXIS])
            y_values.append(transmitter[YAXIS])
            if add_circles and config.TYPE == config.PROTOTYPE:
                circle = plt.Circle((transmitter[XAXIS],transmitter[YAXIS]), 
                    radius=config.MAX_DIST, color='r',fill=False)
                fig.gca().add_artist(circle)
            fig.gca().plot(transmitter[XAXIS],transmitter[YAXIS])

    fig.gca().scatter(x_values, y_values)
    fig.gca().set_ylabel("y [m]")
    plt.gca().set_xlabel("x [m]")
    fig.gca().set_ylim([config.BORDERS[YAXIS],
        config.BORDERS[2 + YAXIS]])
    fig.gca().set_xlim([config.BORDERS[XAXIS],
        config.BORDERS[2 + XAXIS]])
    fig.gca().set_aspect('equal', adjustable='box')

    if config.TYPE == config.RALANS:
        _, _, bdfile = ralans_helper.getFiles(config.FILENAME)
        if add_buildings:
            draw_buildings(plt, (0,0,0), bdfile)

    if add_grid and config.PLACEMENT_TYPE == config.AREA:
        fig.gca().xaxis.set_ticks(np.arange(0.5,config.LENG[XAXIS]-0.5,1))
        fig.gca().yaxis.set_ticks(np.arange(0.5,config.LENG[YAXIS]-0.5,1))
        fig.gca().grid(True,linestyle='solid')
    fig.suptitle('Scatter Plot' + name)

    #add description
    if print_fitness:
        description += "Fitness: " + str(individual.fitness.values)
    fig.text(0.1,0.1,description)

    if save:
        name = "scatter_nodes" + "_" + name 
        fig.savefig(config.FOLDER+name)

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
    for probe in range(config.IND_LEN):
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

def history(his, toolbox, save=True):
    """plot the history of a ga run by showing the mutations.

    :his: the history object from DEAP generated by the genetic algorithm

    """
    print('genealogy_index: ', his.genealogy_index)
    num_of_nodes = his.genealogy_index

    colors = []
    for key, value in his.genealogy_history.items():
        colors.append(toolbox.evaluate(his.genealogy_history[key])[0])

    g = gt.Graph(directed=True) 
    g.add_vertex(num_of_nodes)
    
    for key, parents in his.genealogy_tree.items():
        for parent in parents:
            # print("key: ", key, " type: ", type(key))
            # print("parent: ", parent, " type: ", type(parent))
            g.add_edge(g.vertex(parent-1), g.vertex(key-1))

    name = "general_history" + ".png"
    if save:
        gt.graphviz_draw(g, layout="dot", output=config.FOLDER+name)
        # plt.savefig(config.FOLDER + name)

def draw_buildings(plt, color, bdfile):
    polygons = []
    st = time.time()
    print("Draw buildings...")
    for l in bdfile:
        l = ralans_helper.conv_byte_to_str(l)
        poly = np.loadtxt(io.StringIO(l), delimiter=" ")
        xs = poly[::3]
        ys = poly[1::3]
        assert len(xs) == len(ys)
        zipxy = np.empty((len(xs),2))
        for index, (value1, value2) in enumerate(zip(xs, ys)):
            zipxy[index] = [value1, value2]
        polygonzipxy = Polygon(zipxy, fill=False)
        polygons.append(polygonzipxy)

    c = PatchCollection(np.array(polygons), match_original=True)
    #c.set_hatch("\\\\\\\\")
    c.set_alpha(0.3)
    c.set_facecolor(color)
    c.set_edgecolor(color)
    plt.gca().add_collection(c)

    print("Needed time:", time.time() - st)
    bdfile.close()
