#    This file is part of DEAP.
#
#    DEAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    DEAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with DEAP. If not, see <http://www.gnu.org/licenses/>.

import random

import numpy as np

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

ROWS = 16
COLS = 7

MAX_DIST = 40
REAL_DIST_CELL = 5

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", np.ndarray, shape=(ROWS,COLS), dtype='bool', order='C',
        fitness=creator.FitnessMax)

toolbox = base.Toolbox()

toolbox.register("attr_bool", random.randint, 0, 1)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool,
        n=ROWS*COLS)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def packet_received(ind_index,probe_index):
    """TODO: Docstring for packet_received.

    :ind_index: TODO
    :probe_index: TODO
    :returns: TODO

    """

    dist_cells = np.linalg.norm(np.subtract(ind_index,probe_index))
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
    rec_packs = np.zeros((ROWS,COLS), dtype=np.int, order='C')

    #TODO probably performance improvable
    for ind_index, node in np.ndenumerate(individual):
        if node != 0:
            for probe_index, probe in np.ndenumerate(rec_packs):
                if packet_received(ind_index,probe_index) == True:
                    rec_packs[probe_index] += 1


    # print(rec_packs)
    return rec_packs


def SPNEevaluate(individual):
    print(dir(individual))
    # print(individual.data)
    # for i in individual:
        # print(i)
    nodes = np.count_nonzero(individual)
    print("nodes",nodes)
    spne = received_packets(individual).sum()

    spne /= (nodes * ROWS * COLS)

    spne = spne.item()
    print(spne)
    return spne,

def cxTwoPointCopy(ind1, ind2):
    """Execute a two points crossover with copy on the input individuals. The
    copy is required because the slicing in numpy returns a view of the data,
    which leads to a self overwritting in the swap operation. It prevents
    ::

        >>> import numpy
        >>> a = numpy.array((1,2,3,4))
        >>> b = numpy.array((5.6.7.8))
        >>> a[1:3], b[1:3] = b[1:3], a[1:3]
        >>> print(a)
        [1 6 7 4]
        >>> print(b)
        [5 6 7 8]
    """
    size = len(ind1)
    cxpoint1 = random.randint(1, size)
    cxpoint2 = random.randint(1, size - 1)
    if cxpoint2 >= cxpoint1:
        cxpoint2 += 1
    else: # Swap the two cx points
        cxpoint1, cxpoint2 = cxpoint2, cxpoint1

    ind1[cxpoint1:cxpoint2], ind2[cxpoint1:cxpoint2] \
            = ind2[cxpoint1:cxpoint2].copy(), ind1[cxpoint1:cxpoint2].copy()

    return ind1, ind2


toolbox.register("evaluate", SPNEevaluate)
toolbox.register("mate", cxTwoPointCopy)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)

def main():
    #random.seed()

    pop = toolbox.population(n=300)

    # Numpy equality function (operators.eq) between two arrays returns the
    # equality element wise, which raises an exception in the if similar()
    # check of the hall of fame. Using a different equality function like
    # numpy.array_equal or numpy.allclose solve this issue.
    hof = tools.HallOfFame(1, similar=np.array_equal)

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=1100, stats=stats,
            halloffame=hof)

    return pop, stats, hof

if __name__ == "__main__":
    main()
