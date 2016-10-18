import random
import numpy as np
from operator import attrgetter

def repRandom(pop, offspr, new_pop):
    """replaces randomly.
    :returns: TODO

    """
    rep_idxs = random.sample(list(range(len(pop))), len(offspr))
    for i in range(len(offspr)):
        pop[rep_idxs[i]] = offspr[i]

    return pop

def repParents(pop, offspr, new_pop):
    """replaces the parents by their kids

    :pop: TODO
    :offspr: TODO
    :returns: TODO

    """
    return new_pop

def repTournament(pop, offspr, new_pop, tournsize):
    """ replaces the individuals of the pop using the reverse Tournament
    Selection
    """
    pop_indices = list(range(len(pop)))
    for child in offspr:
        aspirant_indices = random.sample(pop_indices, tournsize)
        aspirants = [pop[j] for j in aspirant_indices]
        min_idx = aspirants.index(min(aspirants, key=attrgetter("fitness")))
        pop[aspirant_indices[min_idx]] = child

    return pop
