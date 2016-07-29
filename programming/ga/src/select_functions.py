import random
import numpy as np
from operator import attrgetter

def selRandom(individuals, k):
    """select k individuals randomly.

    :individuals: TODO
    :k: TODO
    :returns: TODO

    """
    return random.sample(individuals, k)

def selTournament(individuals, k, tournsize):
    """Select *k* individuals from the input *individuals* using *k*
    tournaments of *tournsize* individuals. The list returned contains
    references to the input *individuals*.
    
    :param individuals: A list of individuals to select from.
    :param k: The number of individuals to select.
    :param tournsize: The number of individuals participating in each tournament.
    :returns: A list of selected individuals.
    
    """
    chosen = []
    chosen_indices = []
    individual_indices = list(range(len(individuals)))
    for i in range(k):
        aspirant_indices = selRandom(individual_indices, tournsize)
        aspirants = [individuals[j] for j in aspirant_indices]
        max_index = aspirants.index(max(aspirants, key=attrgetter("fitness")))
        chosen.append(aspirants[max_index])
        chosen_indices.append(aspirant_indices[max_index])
        individual_indices.remove(aspirant_indices[max_index])

    return chosen, chosen_indices
