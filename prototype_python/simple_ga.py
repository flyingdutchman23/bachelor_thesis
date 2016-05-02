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
import array
import matplotlib.pyplot as plt

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

POP_SIZE = 50
GEN_NUMBER = 30

ROWS = 16
COLS = 7

MAX_DIST = 25
REAL_DIST_CELL = 5

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", array.array, typecode='b', fitness=creator.FitnessMax)

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
    rec_packs_plot(rec_packs)
    return rec_packs


def SPNEevaluate(individual):
    print_individual(individual)
    nodes = ROWS * COLS - individual.count(0)
    print("nodes",nodes)

    #if there are no nodes, it can be divided by zero!
    #But the result should be 0
    spne = 0
    if nodes != 0:
        spne = sum(received_packets(individual))
        spne /= (nodes * ROWS * COLS)

    print(spne)
    return spne,

def print_individual(individual):

    print("Individual")
    for r in range(ROWS):
        row = []
        for c in range(COLS):
            row.append(individual[r * COLS + c])
        print(r,row)

def simple_plot(logbook):
    gen = logbook.select("gen")
    fit_mins = logbook.select("min")
    fit_maxs = logbook.select("max")
    fit_avgs = logbook.select("avg")

    import matplotlib.pyplot as plt

    fig, ax1 = plt.subplots()
    print("gen",gen)
    print("fit_mins",fit_mins)
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

    plt.show()

def rec_packs_plot(data):
    
    values = np.reshape(data,(ROWS,COLS))
    plt.imshow(values, vmin=0, vmax=max(data), interpolation="nearest",
            cmap=plt.get_cmap("gnuplot2"), origin="lower")                           
    cb = plt.colorbar()                                                                       
    plt.ylabel("y [m]")                                                                       
    plt.xlabel("x [m]")                                                                       
    cb.set_label("received packets")                                                      
    #TODO save plot
    #plt.savefig(savename)                                                                 

    #show the plot                                                                            
    plt.show()

def nodes_plot(data):

    return None

def nodes_radius_plot(data):

    return None


toolbox.register("evaluate", SPNEevaluate)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.1)
toolbox.register("select", tools.selTournament, tournsize=3)

def main():
    #random.seed()

    pop = toolbox.population(n=POP_SIZE)

    # Numpy equality function (operators.eq) between two arrays returns the
    # equality element wise, which raises an exception in the if similar()
    # check of the hall of fame. Using a different equality function like
    # numpy.array_equal or numpy.allclose solve this issue.
    hof = tools.HallOfFame(1)

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    pop, logbook = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=GEN_NUMBER, stats=stats,
            halloffame=hof)

    print(logbook)
    return pop, logbook, hof

if __name__ == "__main__":
    pop, logbook, hof = main()
    simple_plot(logbook)

