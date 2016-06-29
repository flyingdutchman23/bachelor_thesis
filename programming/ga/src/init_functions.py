#This file will contain different initilization functions
import sys
import numpy as np
import random
import bisect

import config

import spne
from deap import creator
from deap import tools
from deap import base

def normal_random(*args):
    """initializes an individual with just random boolean values

    :returns: the individual

    """

    ind = []

    for i in range(config.IND_LEN):
        ind.append(random.randint(0,1))

    return ind

def corners():
    """initializes an individual with 4 nodes. Each node is placed in the corner of the
    grid.

    :returns: the individual

    """
    # the positions in the order top-left, top-right, bottom-left, bottom-right
    # or in most plots bottom-left, bottom-right, top-left, top-right
    positions = [0, config.LENG[0]-1, config.LENG[0] * (config.LENG[1]-1), config.IND_LEN-1]

    return multiple_nodes(positions)

def one_in_mid():
    """initializes an individual with 1 node placed in the center of the grid. The
    position of the mid is:
    the integer of config.IND_LEN / 2

    :returns: the individual

    """
    return one_node(int(config.IND_LEN / 2))

def multiple_nodes(positions):
    """initializes an individual with multiple nodes at their given position.

    :positions: The positions for all the nodes. It should be an iterable, which contains
    all the positions of the nodes. It has to be an integer, which is in the range
    of 0 and config.IND_LEN-1

    :returns: the individual

    """
    assert all(positions) >= 0
    assert all(positions) < config.IND_LEN
    assert len(positions) <= config.IND_LEN

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
    return [0] * config.IND_LEN

def ones():
    """initializes an individual with just 1s

    :returns: the individual

    """
    return [1] * config.IND_LEN

def fixed_number_random(num_of_nodes):
    """initializes an individual randomly with a given number of nodes

    :num_of_nodes: the number of nodes the individual has

    :returns: the individual

    """

    assert num_of_nodes > 0

    node_positions = random.sample(range(config.IND_LEN),num_of_nodes)
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

    ind = [0] * config.IND_LEN

    for index in range(config.IND_LEN):
        if random.random() <= probability:
            ind[index] = 1

    return ind

def best_samples(args, n=config.POP_SIZE, init=config.INIT):
    """TODO: generates a population of the best individuals out of the number of
    individuals specified by random_size.

    :random_size: the number of individuals to generate randomly
    :pop_size: the size of the population
    :returns: the population as it is needed by the ga

    """
    # Choose init function
    print("INIT_ARG: ", args)
    pop_size = n
    print("POP_SIZE: ", pop_size)
    init_fun = None
    init_args = None
    if init == 3:
        init_fun = normal_random
    elif init == 4:
        num_of_nodes = int(args[1])
        init_args = num_of_nodes
        assert num_of_nodes > 0
        init_fun = fixed_number_random
    else:
        sys.exit('Wrong init function!')

    remaining_inits = int(args[0])
    # the population needs to be smaller than all generated random candidates
    assert remaining_inits > pop_size

    toolbox = base.Toolbox()
    toolbox.register("init", init_fun, init_args)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.init)
    pop = []

    for i in range(pop_size):
       pop.append(toolbox.individual())

    assert len(pop) == pop_size

    remaining_inits -= pop_size

    fitnesss = np.empty(pop_size)

    for i in range(pop_size):
        fitnesss[i] = spne.graph_evaluate(pop[i])[0]

    # sort the population based on the fitness values
    order = np.argsort(fitnesss)
    fitnesss = fitnesss[order]
    pop = [pop[i] for i in order]

    for i in range(remaining_inits):
        print(i)
        new_ind = toolbox.individual()
        new_fit = spne.graph_evaluate(new_ind)

        # if the new fitness is bigger than some of the existing ones
        if new_fit > fitnesss[-1]:
            # insert the new individual fitness and delete the worst one
            pos = bisect.bisect_left(fitnesss, new_fit)
            fitnesss = np.insert(fitnesss, pos, new_fit)
            fitnesss = np.delete(fitnesss, pop_size)

            # insert the new individual and delete the worst one
            pop.insert(pos, new_ind)
            del pop[-1]

    return pop
