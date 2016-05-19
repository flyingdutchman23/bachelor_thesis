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

#from the genetic algorithms package
from deap import algorithms
from deap import base
from deap import creator
from deap import tools

###my modules
#to use the spne metric
import spne
#to have access to the global constants and variables
from config import ROWS, COLS, GEN_NUMBER, POP_SIZE
#to use some util functions
import plot_helper
import print_helper
import init_functions as init
import mate_functions as mate
import mutate_functions as mutate

###Set up genetic algorithm
#specify individual, creation of it
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", array.array, typecode='b', fitness=creator.FitnessMax)

toolbox = base.Toolbox()

#Each gen is initialized with either 0 or 1
# toolbox.register("my_init", init.fixed_number_random, 3)
# toolbox.register("my_init", init.one_in_mid)
# toolbox.register("my_init", init.corners)
toolbox.register("my_init", init.multiple_nodes, [0,3,5,6])
#registers function to init individual
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.my_init)
#how to init hole population -> in list
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

#which functions to use for specific part of ga
toolbox.register("evaluate", spne.graph_dist_evaluate)
toolbox.register("mate", mate.lochert_mate)
toolbox.register("mutate", mutate.lochert_mutate_one)
toolbox.register("select", tools.selTournament, tournsize=3)

def main():
    #to have same random numbers
    #random.seed(POP_SIZE)

    pop = toolbox.population(n=5)

    #plotting
    print("len of pop:",len(pop))
    print_helper.individual(pop[0])
    # plot_helper.map(pop[0],"first_individual_after_init")
    # plot_helper.nodes_with_range(pop[0],"first_individual_after_init")
    # plot_helper.scatter_map_dist(pop[0],"after_init")
    # plot_helper.draw_individual_graph(pop[0],"first_individual_graph_after_init")

    pop, _ = algorithms.eaSimple(pop, toolbox, cxpb=0.0, mutpb=0.9, ngen=9)

    #plotting
    print("len of pop:",len(pop))
    print_helper.individual(pop[0])

    plot_helper.map(pop[0],"first_individual_after_end")
    plot_helper.graph_nodes_with_range(pop[0],"first_individual_after_end")
    plot_helper.scatter_map_dist(pop[0],"after_end")
    plot_helper.draw_individual_graph(pop[0],"first_individual_graph_after_end")

if __name__ == "__main__":
    main()
