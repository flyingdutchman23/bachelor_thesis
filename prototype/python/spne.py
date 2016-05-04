#to calculate the norm
import numpy as np
#to use arrays for calculating the number of received packets
import array
#to use ROWS and COLS from the config module
from config import ROWS, COLS, MAX_DIST, REAL_DIST_CELL

### Currently the calculation is just based on the distance between the cells and the
### RaLANS calculation will be added soon

def set_max_dist(max_dist):
	"""sets a new value for the maximum distance, at wich 2 nodes can communicate

	:max_dist: the maximum distance

	"""
	assert max_dist > 0
	global MAX_DIST
	MAX_DIST = max_dist

def set_real_dist_cell(real_dist_cell):
	"""sets a new value for the real distance between each center of cell, if the
	cells are placed in a grid. So the distance is the distance between neighboured
	cells in the same row or column.

	:real_dist_cell: the real distance between two neighbouring cells

	"""
	assert real_dist_cell > 0
	global REAL_DIST_CELL
	REAL_DIST_CELL = real_dist_cell


def packet_received(ind_index,probe_index):
    """decides wheither a packet from the index in the individual, so the node, reaches
    the probe node, which has the index probe_index. Therefore it calculates the distance
    and compares that to the maximum allowed distance. The function returns true, if the
    distance is below this maximum.

    :ind_index: the index of the node in the individual
    :probe_index: the index of the probe node

    :returns: true, if distance between ind_index and probe_index is smaller than MAX_DIST
              false, else

    """

    ind_row = int(ind_index / COLS)
    ind_col = ind_index % COLS
    probe_row = int(probe_index / COLS)
    probe_col = probe_index % COLS
    dist_cells = np.linalg.norm(np.subtract((ind_row,ind_col),(probe_row,probe_col)))
    dist_cells *= REAL_DIST_CELL

    return dist_cells <= MAX_DIST


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

    #TODO probably performance improvable
    for ind_index, node in enumerate(individual):
        if node != 0:
            for probe_index, probe in enumerate(rec_packs):
                if packet_received(ind_index,probe_index) == True:
                    rec_packs[probe_index] += 1


    # print(rec_packs)
    #map_plot(rec_packs,"received packets")
    # nodes_radius_plot(rec_packs,individual,"nodes with radius")
    return rec_packs


def dist_evaluate(individual):
    """
    computes the value of the SPNE metric for the given individual based on the distance.

    :individual: the individual, for which SPNE as its fitness should calculated

    :returns: the numeric value of the SPNE metric as a float

    """
    # map_plot(individual, "Node Placement")
    nodes = ROWS * COLS - individual.count(0)
    #print("nodes",nodes)

    #if there are no nodes, it can be divided by zero!
    #The result should be 0, if there are no nodes, of course
    spne = 0
    if nodes != 0:
        spne = sum(received_packets(individual))
        spne /= (nodes * ROWS * COLS)

    #print(spne)
    return spne,

def ralans_evaluate(individual):
    """
    computes the value of the SPNE metric for the given individual based on the data from
    RaLaNS

    :individual: the individual, for which SPNE as its fitness should calculated

    :returns: the numeric value of the SPNE metric as a float

    """
    #TODO write the function
    return 0.0
