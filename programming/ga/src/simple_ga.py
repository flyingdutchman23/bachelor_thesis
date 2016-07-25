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
# TODO activate later
import plot_helper
import print_helper
import init_functions as inits
import mate_functions as mates
import mutate_functions as mutates
import ralans_wrapper as ralans


toolbox = base.Toolbox()

#which values to measure for the fitnesses of the individuals
stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register("avg", np.mean)
stats.register("std", np.std)
stats.register("min", np.min)
stats.register("max", np.max)

#specify individual, creation of it
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", array.array, typecode='b', fitness=creator.FitnessMax)

def init():

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
    if config.INIT in [0,1,2]:

        if config.INIT == 0:
            toolbox.register("init", inits.normal_random)
        elif config.INIT == 1:
            num_of_nodes = int(config.INIT_ARG[0])
            assert num_of_nodes > 0
            toolbox.register("init", inits.fixed_number_random, num_of_nodes)
        else:
            prob_to_set_node = float(config.INIT_ARG[0])
            assert prob_to_set_node >= 0.0
            assert prob_to_set_node <= 1.0
            toolbox.register("init", inits.flexible_random, prob_to_set_node)
        #registers function to init individual
        toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.init)
        #how to init hole population -> in list
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    elif config.INIT in [3,4]:
        toolbox.register("population", inits.best_samples, config.INIT_ARG,
                init=config.INIT)
    else:
        sys.exit('Wrong init function!')

    if config.MATE == 0:
        toolbox.register("mate", tools.cxTwoPoint)
    elif config.MATE == 1:
        toolbox.register("mate", tools.cxOnePoint)
    elif config.MATE == 2:
        toolbox.register("mate", mates.lochert_mate)
    else:
        sys.exit('Wrong mate function!')

    if config.MUTATE == 0:
        toolbox.register("mutate", tools.mutFlipBit,
                indpb=config.MUTATE_IND_PROB)
    elif config.MUTATE == 1:
        toolbox.register("mutate", mutates.lochert_mutate_one)
    elif config.MUTATE == 2:
        sys.exit('this option is not implemented yet!')
    else:
        sys.exit('Wrong mutate function!')

    if config.SELECT == 0:
        toolbox.register("select", tools.selTournament, tournsize=3)
    elif config.SELECT == 1:
        sys.exit('this option is not implemented yet!')
    else:
        sys.exit('Wrong select function!')


def run(doSave=True, show=True):
    #to have same random numbers
    # random.seed(config.POP_SIZE)

    his = tools.History()
    toolbox.decorate("mate", his.decorator)
    toolbox.decorate("mutate", his.decorator)

    pop = toolbox.population(n=config.POP_SIZE)

    hof = tools.HallOfFame(config.HOF_NUM)

    pool = multiprocessing.Pool()
    toolbox.register("map", pool.map)

    pop, logbook = algorithms.eaSimple(pop, toolbox, cxpb=config.SELECT_PROB,
            mutpb=config.MUTATE_PROB, 
            ngen=config.GEN_NUM, stats=stats, halloffame=hof)

    if doSave:
        save(hof, logbook, pop, his, show)

def save(hof, logbook, pop, his, show=True, save_his=False):
    """does a lot of stuff after the ga to store data, plot data and the
    Statistics.

    :hof: the hall of fame
    :logbook: the logbook, contains the Statistics
    :pop: the final population
    :his: the history

    """

    my_util.save_node_positions(config.FOLDER+"transmitterposs.txt", hof[0],
            config.POSITIONS)

    my_util.save_dict(config.FOLDER+"history_individuals.ser",
            his.genealogy_history)
    my_util.save_dict(config.FOLDER+"history_tree.ser",
            his.genealogy_tree)

    plot_helper.avg_min_max(logbook)
    plot_helper.scatter_map_dist(hof[0],"best_individual_after_end")
    plot_helper.draw_individual_graph(hof[0],"best_individual_graph")

    if config.PLACEMENT_TYPE == config.AREA and False:
        plot_helper.map(hof[0],"best_individual_after_end")
        plot_helper.graph_nodes_with_range(hof[0],"best_individual_after_end")

    if save_his:
        his.update(pop)
        pprint(vars(his))
        plot_helper.history(his, toolbox)
