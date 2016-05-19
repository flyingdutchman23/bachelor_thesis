#This file will contain different initilization functions

import random

from config import IND_LEN, COLS, ROWS

def normal_random():
    """initializes an individual with just random boolean values

    :returns: the individual

    """

    ind = []

    i = 0
    while i < IND_LEN:
        ind.append(random.randint(0,1))
        i += 1

    return ind

def corners():
    """initializes an individual with 4 nodes. Each node is placed in the corner of the
    grid.

    :returns: the individual

    """
    # the positions in the order top-left, top-right, bottom-left, bottom-right
    # or in most plots bottom-left, bottom-right, top-left, top-right
    positions = [0, COLS-1, COLS * (ROWS-1), IND_LEN-1]

    return multiple_nodes(positions)

def one_in_mid():
    """initializes an individual with 1 node placed in the center of the grid. The
    position of the mid is:
    the integer of IND_LEN / 2

    :returns: the individual

    """
    return one_node(int(IND_LEN / 2))

def multiple_nodes(positions):
    """initializes an individual with multiple nodes at their given position.

    :positions: The positions for all the nodes. It should be an iterable, which contains
    all the positions of the nodes. It has to be an integer, which is in the range
    of 0 and IND_LEN-1

    :returns: the individual

    """
    assert all(positions) >= 0
    assert all(positions) < IND_LEN
    assert len(positions) <= IND_LEN

    ind = zeros()

    for pos in positions:
        ind[pos] = 1

    return ind

def one_node(pos):
    """initializes an individual with exactly 1 node at a given position

    :pos: the position the node should have. It has to be an integer, which is in the range
    of 0 and IND_LEN-1

    :returns: the individual

    """
    return multiple_nodes([pos])

def zeros():
    """initializes an individual with just 0s

    :returns: the individual

    """
    return [0] * IND_LEN

def ones():
    """initializes an individual with just 1s

    :returns: the individual

    """
    return [1] * IND_LEN

def fixed_number_random(num_of_nodes):
    """initializes an individual randomly with a given number of nodes

    :num_of_nodes: the number of nodes the individual has

    :returns: the individual

    """

    assert num_of_nodes > 0

    node_positions = random.sample(range(IND_LEN),num_of_nodes)
    ind = zeros()
    for node_position in node_positions:
        ind[node_position] = 1

    #to check that algorithm works correct
    assert sum(ind) == num_of_nodes

    return ind

def flexible_random(probability):
    """initializes an individual randomly with a given probability to place a node on each
    position

    :probability: the probability to place a node

    :returns: the individual

    """
    assert probability > 0
    assert probability < 1

    ind = [0] * IND_LEN

    for index in range(IND_LEN):
        if random.random() <= probability:
            ind[index] = 1

    return ind
