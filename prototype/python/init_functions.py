#This file will contain different initilization functions

import random

from config import IND_LEN

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

#TODO create init functions for specific, own data

def fixed_number_random(num_of_nodes):
    """initializes an individual randomly with a given number of nodes

    :num_of_nodes: the number of nodes the individual has

    :returns: the individual

    """

    assert num_of_nodes > 0

    return random.sample(range(IND_LEN),num_of_nodes)


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
