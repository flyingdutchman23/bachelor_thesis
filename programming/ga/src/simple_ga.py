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

#from the genetic algorithms package
from deap import algorithms
from deap import base
from deap import creator
from deap import tools

###my modules
#to use the spne metric
import spne
#to have access to the global constants and variables
import config
#to use some util functions
# TODO activate later
import plot_helper
import print_helper
import init_functions as inits
import mate_functions as mates
import mutate_functions as mutates


toolbox = base.Toolbox()

#which values to measure for the fitnesses of the individuals
stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register("avg", np.mean)
stats.register("std", np.std)
stats.register("min", np.min)
stats.register("max", np.max)


def init():
    #specify individual, creation of it
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", array.array, typecode='b', fitness=creator.FitnessMax)

    print('init', config.INIT)
    # Choose init function
    if config.INIT == 0:
        toolbox.register("init", inits.normal_random)
    elif config.INIT == 1:
        num_of_nodes = int(config.INIT_ARG)
        assert num_of_nodes > 0
        toolbox.register("init", inits.fixed_number_random, num_of_nodes)
    elif config.INIT == 2:
        prob_to_set_node = float(config.INIT_ARG)
        assert prob_to_set_node >= 0.0
        assert prob_to_set_node <= 1.0
        toolbox.register("init", inits.flexible_random, prob_to_set_node)
    elif config.INIT == 3:
        sys.exit('this option is not implemented yet!')
    elif config.INIT == 4:
        sys.exit('this option is not implemented yet!')
    else:
        sys.exit('Wrong init function!')

    #registers function to init individual
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.init)
    #how to init hole population -> in list
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    
    #which functions to use for specific part of ga
    if config.FITNESS == 0:
        toolbox.register("evaluate", spne.graph_dist_evaluate)
    elif config.FITNESS == 1:
        sys.exit('this option is not implemented yet!')
    else:
        sys.exit('Wrong fitness function!')

    if config.MATE == 0:
        toolbox.register("mate", tools.cxTwoPoint)
    elif config.MATE == 1:
        toolbox.register("mate", tools.cxOnePoint)
    elif config.MATE == 2:
        toolbox.register("mate", mates.lochert_mate)
    else:
        sys.exit('Wrong mate function!')

    if config.MUTATE == 0:
        toolbox.register("mutate", tools.mutFlipBit, indpb=0.1)
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


def run():
    #to have same random numbers
    # random.seed(config.POP_SIZE)

    pop = toolbox.population(n=config.POP_SIZE)

    print("len of pop:",len(pop))
    print_helper.individual(pop[0])

    # for i in range(config.POP_SIZE):
        # title = "individual after init, nodes: " + str(sum(pop[i]))
        # plot_helper.map(pop[i],title)

    hof = tools.HallOfFame(config.HOF_NUM)
    pop, logbook = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.1, 
            ngen=config.GEN_NUM, stats=stats, halloffame=hof)

    print("len of pop:",len(pop))

    print_helper.individual(pop[0])
    plot_helper.avg_min_max(logbook)
    plot_helper.map(hof[0],"best_individual_after_end")
    plot_helper.graph_nodes_with_range(hof[0],"best_individual_after_end")

    plot_helper.scatter_map_dist(hof[0],"best_individual_after_end")
    plot_helper.draw_individual_graph(hof[0],"best_individual_graph")
    print_helper.individual(hof[0])

    #TODO save the information somewhere
    return pop, logbook, hof
