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

def combine_plots(logbooks, selects, descs, save_folder, to_show=True, col=0, 
        name = "Statistics", title="No_Titel", yaxis='SPNE', 
        xaxis='Generation'):

    colors = ['b', 'g', 'r', 'y', 'c', 'm', 'orange', 'brown']
    assert col in [0,1]
    print('len logbooks: ', len(logbooks))
    print('len selects: ', len(selects))
    print('len descs: ', len(descs))
    assert len(logbooks) == len(selects) == len(descs)

    data = [None] * len(logbooks)

    gen = np.array(logbooks[0].select("gen"))
    for i in range(len(logbooks)):
        gen_new = np.array(logbooks[i].select("gen"))
        # assert set(gen) <= set(gen_new)
        data[i] = np.array(logbooks[i].select(selects[i]))[:,col]
        if len(gen_new) > len(gen):
            data[i] = data[i][:len(gen)]

    fig, ax1 = plt.subplots()

    lines = [None] * len(logbooks)
    # data[0] = np.insert(data[0], 0, 0)
    # gen = [0] + gen[:]
    # gen = np.append(gen, gen[-1] + 1)
    for i in range(len(logbooks)):
        lines[i] = ax1.plot(gen, data[i], colors[i], label=descs[i])

    ax1.set_xlabel(xaxis)
    ax1.set_ylabel(yaxis)
    ax1.set_ylim([0,1])

    # not sure what's that for
    # for tl in ax1.get_yticklabels():
        # tl.set_color("b")

    lns = []
    for l in lines:
        lns += l

    labs = [l.get_label() for l in lns]
    # ax1.legend(lns, labs, loc="best", title=title)
    # ax1.legend(lns, labs, title=title, bbox_to_anchor=(1.05, 1), loc='best', 
            # borderaxespad=0.)
    # ax1.legend(lns, labs, title=title, bbox_to_anchor=(0., 1.02, 1., .102),
            # loc=3, ncol=3, mode="expand", borderaxespad=0.)
    fig.subplots_adjust(top=0.83, bottom=0.09, left=0.08, right=0.95)

    #save the plot
    fig.savefig(save_folder+name + '.eps')
    if to_show:
        plt.show()

def bar_plot(logbooks, selects, descs, save_folder, to_show=True, col=0, 
        name = "Statistics", title="No_Titel", max_evals=100000):

    assert col in [0,1]
    assert len(logbooks) == len(selects) == len(descs)
    N = len(logbooks)
    
    data = [None] * N
    evals_data = [None] * N
    tot_evals = []

    gen = np.array(logbooks[0].select("gen"))
    for i in range(len(logbooks)):
        gen_new = np.array(logbooks[i].select("gen"))
        assert set(gen) == set(gen_new)
        evals_data[i] = np.array(logbooks[i].select('nevals'))
        tot_evals.append(np.sum(evals_data[i]))
        data[i] = np.array(logbooks[i].select(selects[i]))[:,col]

    print(tot_evals)
    min_evals = min(tot_evals)
    if min_evals > max_evals:
        min_evals = max_evals
    print(min_evals)

    for i in range(len(logbooks)):
        evals = 0
        j = 0
        while evals <= min_evals and j < len(evals_data[i]):  
            evals += evals_data[i][j]
            j += 1
        assert j != len(evals_data[i]) or evals == min_evals
        print('j: ', j)
        print('evals: ', evals-evals_data[i][j%len(evals_data[i])])
        data[i] = data[i][:j]
            

    # just take the last value of the logbooks
    values = [None] * N
    for i in range(N):
        values[i] = data[i][-1]
    print(values)

    width = 0.25       # the width of the bars
    ind = np.arange(N)  # the x locations for the groups
    ind = ind + width/2

    
    fig, ax = plt.subplots()
    rects1 = ax.bar(ind, values, width, color='r')
    
    # add some text for labels, title and axes ticks
    ax.set_ylabel('Fitness')
    ax.set_xlabel(title)
    # ax.set_title('Scores by group and gender')
    ax.set_xticks(ind + width/2)
    ax.set_xticklabels(descs)
    
    
    autolabel(rects1, ax)
    
    fig.subplots_adjust(top=0.92, bottom=0.12, left=0.05, right=0.95)

    #save the plot
    fig.savefig(save_folder + name + '.eps')
    if to_show:
        plt.show()

def box_plot(logbookss, selects, descs, save_folder, to_show=True, col=0, 
        name = "Statistics", title="No_Titel", max_evals=100000,
        comp_by_evals=True, yaxis='SPNE', comp_by_gens=False, 
        xaxis='Generation'):

    assert col in [0,1]
    assert len(logbookss) == len(selects) == len(descs)
    N = len(logbookss)
    
    data = [None] * N
    evals_data = [None] * N
    tot_evals = []
    min_gens = []

    for i in range(len(logbookss)):

        data[i] = []
        evals_data[i] = []
        logbooks = logbookss[i]
        gen = np.array(logbookss[i][0].select("gen"))
        tot_evals_one = []

        for j in range(len(logbooks)):
            gen_new = np.array(logbooks[j].select("gen"))
            if len(gen_new) < len(gen):
                gen = gen_new
        min_gens.append(gen)

        for j in range(len(logbooks)):
            gen_new = np.array(logbooks[j].select("gen"))
            assert set(gen) <= set(gen_new)
            # assert set(gen) == set(gen_new)
            cur_evals_data = np.array(logbooks[j].select('nevals'))
            cur_data = np.array(logbooks[j].select(selects[i]))[:,col]
            if len(gen_new) > len(gen) and comp_by_gens:
                cur_evals_data = cur_evals_data[:len(gen)]
                cur_data = cur_data[:len(gen)]
            evals_data[i].append(cur_evals_data)
            tot_evals_one.append(np.sum(evals_data[i][j]))
            data[i].append(cur_data)

        tot_evals.append(np.mean(tot_evals_one))

    print("total evals:")
    print(tot_evals)
    # tot_evals[-1] = 19650

    if comp_by_evals:
        print("equalize!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        min_evals = min(tot_evals)
        if min_evals > max_evals:
            min_evals = max_evals
        print(min_evals)

        for k in range(len(logbookss)):
            logbooks = logbookss[k]
            for i in range(len(logbooks)):
                evals = 0
                j = 0
                while evals <= min_evals and j < len(evals_data[k][i]):  
                    # print("in loop begin")
                    evals += evals_data[k][i][j]
                    j += 1
                    # print(evals_data[i][j])
                    # print("in loop end")
                # assert j != len(evals_data[k][i]) or evals == min_evals
                # print('j: ', j)
                # print('evals: ', evals-evals_data[k][i][j%len(evals_data[k][i])])
                data[k][i] = data[k][i][:j]
            

    # just take the last value of the logbooks
    values = [None] * N
    for i in range(N):
        values[i] = []
        for j in range(len(logbookss[i])):
            end = len(data[i][j])
            print('evals: ', sum(evals_data[i][j][:end]))
            values[i].append(data[i][j][-1])
    print(values)

    width = 0.25       # the width of the bars
    ind = np.arange(N)  # the x locations for the groups
    ind = ind + width/2

    
    fig, ax = plt.subplots()
    ax.boxplot(values, labels=descs, showmeans=True)

    fig, ax = plt.subplots()
    rects1 = ax.bar(ind, tot_evals, width, color='r')
    # ax.set_title(title)
    # rects1 = ax.bar(ind, values, width, color='r')
    
    # add some text for labels, title and axes ticks
    ax.set_ylabel(yaxis)
    ax.set_xlabel(xaxis)
    # ax.set_xticks(ind + width/2)
    # ax.set_xticklabels(descs)
    
    
    # autolabel(rects1, ax)
    
    fig.subplots_adjust(top=0.92, bottom=0.12, left=0.09, right=0.95)

    #save the plot
    fig.savefig(save_folder+name + '.eps')
    if to_show:
        plt.show()

def autolabel(rects, ax):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                '%.2f' % float(height),
                ha='center', va='bottom')

def avg_min_max(logbook,save=True,to_show=True, col=0, name = "Statistics"):

    assert col in [0,1]

    gen = np.array(logbook.select("gen"))
    fit_mins = np.array(logbook.select("min"))[:,col]
    fit_maxs = np.array(logbook.select("max"))[:,col]
    fit_avgs = np.array(logbook.select("avg"))[:,col]
    fit_hof = np.array(logbook.select("hof_max"))[:,col]

    fig, ax1 = plt.subplots()
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
