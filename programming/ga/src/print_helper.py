
### helper module to print specific states and results via normal print on terminal

from constants import XAXIS, YAXIS, LIST
import config

def individual(individual):

    print("Individual, nodes: ",sum(individual))
    if config.PLACEMENT_TYPE == LIST:
        print(individual)
    else:
        for r in range(config.LENG[YAXIS]):
            row = []
            for c in range(config.LENG[XAXIS]):
                row.append(individual[r * config.LENG[0] + c])
            print(r,row)

def individual_plotorder(individual):

    print("Individual, nodes: ",sum(individual))
    for r in range(config.LENG[1]-1,-1,-1):
        row = list(individual[r*config.LENG[0]:(r+1)*config.LENG[0]])
        print(r,row)

def population(pop):
    """print the complete population.

    :pop: the population to print

    """
    for i in range(len(pop)):
        print('Individual nr. ', i)
        individual(pop[i])
