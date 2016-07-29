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
import plot_helper
import print_helper
import init_functions as inits
import mate_functions as mates
import mutate_functions as mutates
import select_functions as selects
import replace_functions as replaces
import ralans_wrapper as ralans


toolbox = base.Toolbox()

#which values to measure for the fitnesses of the individuals
stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register("avg", np.mean)
stats.register("std", np.std)
stats.register("min", np.min)
stats.register("max", np.max)

hof_stats = tools.Statistics(lambda ind: ind.fitness.values)
hof_stats.register("hof_max", np.max)


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
        toolbox.register("select", selects.selTournament, tournsize=3)
    elif config.SELECT == 1:
        sys.exit('this option is not implemented yet!')
    else:
        sys.exit('Wrong select function!')

    if config.REPLACE == 0:
        toolbox.register("replace", replaces.repTournament, tournsize=3)
    elif config.SELECT == 1:
        toolbox.register("replace", replaces.repParents)
    elif config.SELECT == 2:
        toolbox.register("replace", replaces.repRandom)
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

    pop, logbook = eaSimple(pop, toolbox, cxpb=config.SELECT_PROB,
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

def eaSimple(pop, toolbox, cxpb, mutpb, ngen, stats=None,
             halloffame=None, verbose=__debug__):
    """This algorithm reproduce the simplest evolutionary algorithm as
    presented in chapter 7 of [Back2000]_.
    
    :param pop: A list of individuals.
    :param toolbox: A :class:`~deap.base.Toolbox` that contains the evolution
                    operators.
    :param cxpb: The probability of mating two individuals.
    :param mutpb: The probability of mutating an individual.
    :param ngen: The number of generation.
    :param stats: A :class:`~deap.tools.Statistics` object that is updated
                  inplace, optional.
    :param halloffame: A :class:`~deap.tools.HallOfFame` object that will
                       contain the best individuals, optional.
    :param verbose: Whether or not to log the statistics.
    :returns: The final population and a :class:`~deap.tools.Logbook`
              with the statistics of the evolution.
    
    The algorithm takes in a population and evolves it in place using the
    :meth:`varAnd` method. It returns the optimized population and a
    :class:`~deap.tools.Logbook` with the statistics of the evolution (if
    any). The logbook will contain the generation number, the number of
    evalutions for each generation and the statistics if a
    :class:`~deap.tools.Statistics` if any. The *cxpb* and *mutpb* arguments
    are passed to the :func:`varAnd` function. The pseudocode goes as follow
    ::

        evaluate(population)
        for g in range(ngen):
            population = select(population, len(population))
            offspring = varAnd(population, toolbox, cxpb, mutpb)
            evaluate(offspring)
            population = offspring

    As stated in the pseudocode above, the algorithm goes as follow. First, it
    evaluates the individuals with an invalid fitness. Second, it enters the
    generational loop where the selection procedure is applied to entirely
    replace the parental population. The 1:1 replacement ratio of this
    algorithm **requires** the selection procedure to be stochastic and to
    select multiple times the same individual, for example,
    :func:`~deap.tools.selTournament` and :func:`~deap.tools.selRoulette`.
    Third, it applies the :func:`varAnd` function to produce the next
    generation population. Fourth, it evaluates the new individuals and
    compute the statistics on this population. Finally, when *ngen*
    generations are done, the algorithm returns a tuple with the final
    population and a :class:`~deap.tools.Logbook` of the evolution.

    .. note::

        Using a non-stochastic selection method will result in no selection as
        the operator selects *n* individuals from a pool of *n*.
    
    This function expects the :meth:`toolbox.mate`, :meth:`toolbox.mutate`,
    :meth:`toolbox.select` and :meth:`toolbox.evaluate` aliases to be
    registered in the toolbox.
    
    .. [Back2000] Back, Fogel and Michalewicz, "Evolutionary Computation 1 :
       Basic Algorithms and Operators", 2000.
    """
    hof_fit = None

    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals']\
            + (stats.fields if stats else [])\
            + (hof_stats.fields if hof_stats else [])

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in pop if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    halloffame.update(pop)

    record = stats.compile(pop) if stats else {}
    hof_record = hof_stats.compile(halloffame) if hof_stats else {}
    record.update(hof_record)
    logbook.record(gen=0, nevals=len(invalid_ind), **record)
    if verbose:
        print(logbook.stream)

    # Begin the generational process
    for gen in range(1, ngen+1):

        # Select the next generation individuals
        # round it to an even number, because uneven is unnecessary for
        # crossover
        offspr_size = int(len(pop) * cxpb) & (-2)
        _, offspr_idxs = toolbox.select(pop, offspr_size)
        offspr = [toolbox.clone(ind) for ind in pop]

        # Apply crossover and mutation on the offspring
        for i in range(0,len(offspr_idxs),2):
            offspr[offspr_idxs[i-1]], offspr[offspr_idxs[i]] = toolbox.mate(
                    offspr[offspr_idxs[i-1]], offspr[offspr_idxs[i]])
            del offspr[offspr_idxs[i-1]].fitness.values,\
                    offspr[offspr_idxs[i]].fitness.values

        for i in range(len(offspr)):
            if random.random() < mutpb:
                offspr[i], = toolbox.mutate(offspr[i])
                del offspr[i].fitness.values
        
        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspr if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        
        # Update the hall of fame with the generated individuals
        halloffame.update(invalid_ind)

        pop[:] = toolbox.replace(pop, invalid_ind, offspr)

        # Append the current generation statistics to the logbook
        record = stats.compile(pop) if stats else {}
        hof_record = hof_stats.compile(halloffame) if hof_stats else {}
        record.update(hof_record)
        logbook.record(gen=gen, nevals=len(invalid_ind), **record)
        if verbose:
            print(logbook.stream)        

    return pop, logbook
