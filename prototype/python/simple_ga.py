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

###Set up genetic algorithm
#specify individual, creation of it
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", array.array, typecode='b', fitness=creator.FitnessMax)

toolbox = base.Toolbox()

#Each gen is initialized with either 0 or 1
toolbox.register("attr_bool", random.randint, 0, 1)
#registers function to init individual
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool,
        n=ROWS*COLS)
#how to init hole population -> in list
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

#which functions to use for specific part of ga
toolbox.register("evaluate", spne.dist_evaluate)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.1)
toolbox.register("select", tools.selTournament, tournsize=3)

#which values to measure for the fitnesses of the individuals
stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register("avg", np.mean)
stats.register("std", np.std)
stats.register("min", np.min)
stats.register("max", np.max)

def main():
    #to have same random numbers
    random.seed(POP_SIZE)

    pop = toolbox.population(n=POP_SIZE)
    hof = tools.HallOfFame(1)
    pop, logbook = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=GEN_NUMBER, 
            stats=stats, halloffame=hof)

    plot_helper.avg_min_max(logbook)

    plot_helper.scatter_map_dist(hof[0])
    return pop, logbook, hof

if __name__ == "__main__":
    pop, logbook, hof = main()
