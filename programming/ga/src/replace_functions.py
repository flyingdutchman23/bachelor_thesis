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
    """Select *k* individuals from the input *individuals* using *k*
    tournaments of *tournsize* individuals. The list returned contains
    references to the input *individuals*.
    
    :param individuals: A list of individuals to select from.
    :param k: The number of individuals to select.
    :param tournsize: The number of individuals participating in each tournament.
    :returns: A list of selected individuals.
    
    """
    pop_indices = list(range(len(pop)))
    for child in offspr:
        aspirant_indices = random.sample(pop_indices, tournsize)
        aspirants = [pop[j] for j in aspirant_indices]
        min_idx = aspirants.index(min(aspirants, key=attrgetter("fitness")))
        pop[aspirant_indices[min_idx]] = child

    return pop
