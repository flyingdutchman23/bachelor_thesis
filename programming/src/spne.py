#to calculate the norm
import numpy as np
#to use arrays for calculating the number of received packets
import array
#to use config.LENG[1] and config.LENG[0] from the config module
import config
#to plot for testing
# TODO activate
# import plot_helper
#to print individual for debug
import print_helper
#to use a Graph to compute the SPNE fitness, to simulate Multi-Hop
import graph_tool.all as gt

import my_util
#to evaluate with RaLaNS
import ralans_wrapper as ralans

def packet_received(ind_index, probe_index):
    """checks whether there is a connection from the probe node to the node in the
    individual and returns the result as boolean. Handles the RaLaNS and the prototype way
    of calculation by calling the right function based on the config.
    :returns: True, if there is a connection.
              False, if there is no connection.

    """
    
    if config.TYPE == config.PROTOTYPE:
        return prototype_packet_received(ind_index, probe_index)
    else:
        return ralans.packet_received_by_id(ind_index, probe_index)

def prototype_packet_received(ind_index,probe_index):
    """decides wheither a packet from the index in the individual, so the node, reaches
    the probe node, which has the index probe_index. Therefore it calculates the distance
    and compares that to the maximum allowed distance. The function returns true, if the
    distance is below this maximum.

    :ind_index: the index of the node in the individual
    :probe_index: the index of the probe node

    :returns: true, if distance between ind_index and probe_index is smaller than config.MAX_DIST
              false, else

    """

    ind = config.POSITIONS[ind_index]
    probe = config.POSITIONS[probe_index]
    dist_cells = np.linalg.norm(np.subtract(ind,probe))

    return dist_cells <= config.MAX_DIST


def received_packets(individual):
    """computes the number of received packets for the given individual.
    The number of received packets is currently just based on the distance of the probe
    node to all the placed nodes of the individual. The probe node is placed on every
    position.

    :individual: the individual, for which the received_packets should be computed

    :returns: an ndarray containing the number of received packets in each item

    """

    #array for received packets
    rec_packs = array.array('I', [0] * len(individual))
    #array for indices of node positions
    nodes = np.nonzero(individual)[0]
    # print_helper.individual(individual)

    #TODO probably performance improvable
    for node_index in nodes:
        for probe_index in range(len(individual)):
            if packet_received(node_index,probe_index):
                rec_packs[probe_index] += 1


    # print(rec_packs)
    # plot_helper.map(individual,"individual in current calc")
    # plot_helper.map(rec_packs,"received packets")
    # nodes_radius_plot(rec_packs,individual,"nodes with radius")
    return rec_packs, len(nodes)

def graph_received_packets(individual, nodes=None):
    """
    computes the number of received packets for the given individual.
    The number of received packets is currently just based on the distance of the probe
    node to all the placed nodes of the individual. The probe node is placed on every
    position.

    :individual: the individual, for which the received_packets should be computed
    :nodes: the indices(positions) of the nodes, will be computed, if not given, so
    default value is None

    :returns: an ndarray containing the number of received packets in each item

    """

    # number of received packets
    # is initialized with this number, because connections to itself do not count, but
    # will be counted in the algorithm, so they are subtracted before to equalize it.
    num_received_packets = -config.IND_LEN

    # array for indices of node positions
    # computes the positions of the nodes, if they are not given
    if nodes is None:
        nodes = np.nonzero(individual)[0]

    # build the Graph to store the nodes
    g = build_graph(nodes)

    # add probe node to graph
    probe_node = g.add_vertex()
    # probe node iterates over grid. Probe node is added to graph, reachable vertexes are
    # computed and summed up
    for probe in range(config.IND_LEN):
        for node_index, node in enumerate(nodes):
            if packet_received(probe, node) and packet_received(node, probe):
                g.add_edge(probe_node,g.vertex(node_index))
        labeling = gt.label_out_component(g,probe_node)
        num_received_packets += sum(labeling.a)
        g.clear_vertex(probe_node)

    # otherwise something totally wrong
    assert num_received_packets >= 0

    return num_received_packets

def build_graph(nodes):
    """builds the graph for the individual with the given positions of the nodes

    :nodes: an iterable of the positions of the nodes
    :returns: the Graph object

    """
    g = gt.Graph(directed=False)

    num_of_nodes = len(nodes)
    g.add_vertex(num_of_nodes)

    #build Graph by adding an edge between the nodes, which are connected
    for node_index1, node1 in enumerate(nodes):
        for node_index2 in range((node_index1+1),num_of_nodes):
            node2 = nodes[node_index2]
            if packet_received(node1,node2) and packet_received(node2,node1):
                g.add_edge(g.vertex(node_index1),g.vertex(node_index2))

    return g

def graph_evaluate(individual):
    """

    computes the value of the SPNE metric for the given individual based on the distance
    or the RaLaNS data. Which data(distance or RaLaNS) is used is specified in the config 
    module.

    :individual: the individual, for which SPNE as its fitness should calculated
    :returns: a tuple of the numeric value of the SPNE metric as a float and the
    number of nodes

    """
    nodes = np.nonzero(individual)[0]
    return nodes_graph_evaluate(nodes, individual)

def nodes_graph_evaluate(nodes, individual = None):
    """computes the SPNE metric with the given node indices

    :nodes: the node indices
    :returns: a tuple of the numeric value of the SPNE metric as a float and the
    number of nodes

    """
    num_of_nodes = len(nodes)
    if num_of_nodes == 0:
        return 0, num_of_nodes

    rec_packs = graph_received_packets(individual,nodes)
    assert config.IND_LEN == config.LENG[1] * config.LENG[0]
    spne = rec_packs / (num_of_nodes * config.IND_LEN)

    #check boundaries of the SPNE metric
    assert spne <= 1
    assert spne >= 0

    return spne, num_of_nodes
