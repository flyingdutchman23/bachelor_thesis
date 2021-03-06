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
stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register("avg", np.mean, axis=0)
stats.register("std", np.std, axis=0)
stats.register("min", np.amin, axis=0)
stats.register("max", np.amax, axis=0)

hof_stats = tools.Statistics(lambda ind: ind.fitness.values)
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
        num_of_nodes = int(config.INIT_ARG[0])
        print('num_of_nodes: ', num_of_nodes)
        assert num_of_nodes > 0
        toolbox.register("init", inits.fixed_number_random, num_of_nodes)
        #registers function to init individual
        toolbox.register("individual", tools.initIterate, creator.Individual,
                toolbox.init)
        #how to init hole population -> in list
        toolbox.register("population", tools.initRepeat, list,
                toolbox.individual)
    else:
        sys.exit('Wrong init function!')


def run(doSave=True, show=True):

    hof = tools.HallOfFame(config.HOF_NUM)

    pool = multiprocessing.Pool()
    toolbox.register("map", pool.map)

    hof, logbook = random_search(None, toolbox, halloffame=hof,
            stats=stats)

    if doSave:
        save(hof, logbook, show)

def save(pop, logbook, show=False):
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


def random_search(pop, toolbox, stats=None,
             halloffame=None, verbose=__debug__):
    """This algorithm is my simple random search.
    
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

    # Begin the generational process
    evaluations = 0
    iter_evaluations = 0
    gen = 0

    while evaluations < config.GEN_NUM:

        # just a different kind of count, should be the same here
        assert iter_evaluations == evaluations

        # Evaluate the generated neighbours
        print("evaluate...")
        new_inds = toolbox.population(n=config.POP_SIZE)
        fitnesses = toolbox.map(toolbox.evaluate, new_inds)
        for ind, fit in zip(new_inds, fitnesses):
            ind.fitness.values = fit

        evaluations += len(new_inds)
        print("evaluations: ", evaluations)

        halloffame.update(new_inds)
        new_num = int(halloffame[0].fitness.values[1])
        spne = halloffame[0].fitness.values[0]
        assert spne <= 1
        assert new_num > 1

        if spne >= 1:
            # in the fixed version it should not be able to go here, if the
            # number of nodes is small enough that it does not cover the hole
            # area
            toolbox.register("init", inits.fixed_number_random, new_num-1)
            #registers function to init individual
            toolbox.register("individual", tools.initIterate,
                    creator.Individual, toolbox.init)
            #how to init hole population -> in list
            toolbox.register("population", tools.initRepeat, list,
                    toolbox.individual)

        # Append the current generation statistics to the logbook
        for new_ind in new_inds:
            iter_evaluations += 1
            record = stats.compile([new_ind]) if stats else {}
            hof_record = hof_stats.compile(halloffame) if hof_stats else {}
            record.update(hof_record)
            logbook.record(gen=iter_evaluations, nevals=1, time=time.time(),
                    **record)
        if verbose:
            print(logbook.stream)

    return halloffame, logbook


def main():
    args = parser.parse_args()
    config.fill_config(args.configfile)
    init()
    print("after init!!!")
    print()
    run(show=args.show)

    
if __name__ == "__main__":
    main()
