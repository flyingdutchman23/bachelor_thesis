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

import time
import argparse
#to randomize the initilization part
import random
#for easiert calculation
import numpy as np
#to use arrays for the gen sequence, individual
import array
# to exit program if mistake occurs
import sys
# to check content of a variable
from pprint import pprint
# to parallelize computation
import multiprocessing

#from the genetic algorithms package
from deap import algorithms
from deap import base
from deap import creator
from deap import tools

###my modules
#to use the spne metric
import spne
#to have access to the global constants and variables
from constants import RALANS
import config
#to use some util functions
import my_util
import plot_helper
import print_helper
import init_functions as inits
import ralans_wrapper as ralans

parser = argparse.ArgumentParser(
    description='Start the local search with the given config file.')
parser.add_argument('configfile', metavar='C', type=str,
                            help='the path to the config file')
parser.add_argument('--show', dest='show', action='store_true',
                            help='shows the result at end')
parser.add_argument('--no-show', dest='show', action='store_false',
                            help='does not show the result at end')
parser.set_defaults(show=True)

toolbox = base.Toolbox()

#which values to measure for the fitnesses of the individuals
stats = tools.Statistics(lambda ind: ind)
stats.register("avg", np.mean, axis=0)
stats.register("std", np.std, axis=0)
stats.register("min", np.amin, axis=0)
stats.register("max", np.amax, axis=0)

hof_stats = tools.Statistics(lambda ind: ind)
hof_stats.register("hof_max", np.amax, axis=0)


# specify individual, creation of it
# just default, so that it works with parallel
creator.create("MYFIT", base.Fitness, weights=(0.0,))
creator.create("Individual", array.array, typecode='b', fitness=creator.MYFIT)

def init():

    creator.create("MYFIT", base.Fitness, weights=config.WEIGHTS)
    creator.create("Individual", array.array, typecode='b',
            fitness=creator.MYFIT)

    #which functions to use for specific part of ga
    if config.FITNESS == 0:
        if config.TYPE == RALANS:
            ralans.init()
        toolbox.register("evaluate", spne.graph_evaluate)
    elif config.FITNESS == 1:
        sys.exit('this option is not implemented yet!')
    else:
        sys.exit('Wrong fitness function!')

    # Choose init function
    if config.INIT == 0:
        toolbox.register("init", inits.zeros)
        #registers function to init individual
        toolbox.register("individual", tools.initIterate, creator.Individual,
                toolbox.init)
        #how to init hole population -> in list
        toolbox.register("population", tools.initRepeat, list,
                toolbox.individual)
    else:
        sys.exit('Wrong init function!')


def run(doSave=True, show=True):

    pop = toolbox.population(n=config.POP_SIZE)

    # hof = tools.HallOfFame(config.HOF_NUM)

    pool = multiprocessing.Pool()
    toolbox.register("map", pool.map)

    nodes, fit, logbook = local_search(pop, toolbox, stats=stats)

    toolbox.register("init", inits.multiple_nodes, nodes)
    toolbox.register("individual", tools.initIterate, creator.Individual,
            toolbox.init)
    #how to init hole population -> in list
    toolbox.register("population", tools.initRepeat, list,
            toolbox.individual)
    pop = toolbox.population(n=1)
    print("pop: ")
    print(pop)


    if doSave:
        save(pop, logbook, show)

def save(pop, logbook, show=True):
    """does a lot of stuff after the ga to store data, plot data and the
    Statistics.

    :pop: the hall of fame
    :logbook: the logbook, contains the Statistics
    :pop: the final population
    :his: the history

    """

    my_util.save_node_positions(config.FOLDER+"transmitterposs.txt", pop[0],
            config.POSITIONS)
    my_util.save_ind(config.FOLDER+"best_ind.ser", pop[0])
    my_util.save_ind_txt(config.FOLDER+"best_ind.txt", pop[0])

    my_util.save_logbook(config.FOLDER+"logbook.ser", logbook)
    plot_helper.avg_min_max(logbook, col=0, name='spne_stats', to_show=show)
    plot_helper.avg_min_max(logbook, col=1, name='number_of_nodes_stats',
            to_show=show)
    plot_helper.scatter_map_dist(pop[0],"best_individual_after_end",
            to_show=show)
    plot_helper.draw_individual_graph(pop[0],"best_individual_graph")


def local_search(pop, toolbox, stats=None,
             halloffame=None, verbose=__debug__):
    """This algorithm is my simple local search for the flexible version.
    
    :param pop: A list of individuals.
    :param toolbox: A :class:`~deap.base.Toolbox` that contains the evolution
                    operators.
    :param stats: A :class:`~deap.tools.Statistics` object that is updated
                  inplace, optional.
    :param halloffame: A :class:`~deap.tools.HallOfFame` object that will
                       contain the best individuals, optional.
    :param verbose: Whether or not to log the statistics.
    :returns: The final population and a :class:`~deap.tools.Logbook`
              with the statistics of the evolution.
    
    """
    
    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals', 'time']\
            + (stats.fields if stats else [])\
            + (hof_stats.fields if hof_stats else [])

    # Evaluate the individuals with an invalid fitness
    fitnesses = toolbox.map(toolbox.evaluate, pop)
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    # halloffame.update(pop)

    # Begin the generational process
    finished = False
    nodes = list(np.nonzero(pop[0])[0])
    current_fit = pop[0].fitness.values[0]
    assert len(nodes) == 0
    assert current_fit == 0
    gen = 0
    evaluations = 0

    while not finished:

        print("gen: ", gen)

        neighbours = get_neighbours(list(nodes))
        print('current: ', nodes)

        # Evaluate the generated neighbours
        evaluations += len(neighbours)
        print("evaluate")
        fitnesses = toolbox.map(spne.nodes_graph_evaluate, neighbours)
        print("evaluations: ", evaluations)
        # get the best neighbour
        fits = np.array(fitnesses)[:,0]
        max_idx = np.argmax(fits)

        new_fit = fits[max_idx]
        print('current fit: ', current_fit)
        print('new fit: ', new_fit)
        print('new fit in list: ', fitnesses[max_idx])
        print('best neighbour: ', neighbours[max_idx])
        print('current: ', nodes)
        if new_fit > current_fit:
            current_fit = new_fit
            # get the new node positions
            nodes = neighbours[max_idx]
            if new_fit >= 1:
                finished = True

        # Append the current generation statistics to the logbook
        record = stats.compile(fitnesses) if stats else {}
        hof_record = hof_stats.compile([fitnesses[max_idx]]) if hof_stats\
                else {}
        record.update(hof_record)
        logbook.record(gen=gen, nevals=len(fitnesses), time=time.time(),
                **record)
        if verbose:
            print(logbook.stream)        
        gen += 1

    return nodes, current_fit, logbook

def get_neighbours(nodes):
    """get all neighbours

    :ind: TODO
    :node_idx: TODO
    :returns: TODO

    """
    # get relevant neighbour positions
    poss = set(range(config.IND_LEN)) 
    poss = filter_list(poss, nodes)

    neighbours = []
    for pos in poss:
        neighbour = list(nodes)
        neighbour.append(pos)
        assert len(neighbour) == len(nodes)+1
        neighbours.append(neighbour)

    print("got all neighbours")
    return neighbours

def filter_list(full_list, excludes):
    s = set(excludes)
    return (x for x in full_list if x not in s)


def main():
    args = parser.parse_args()
    config.fill_config(args.configfile)
    init()
    print("after init!!!")
    print()
    run(show=args.show)

    
if __name__ == "__main__":
    main()
