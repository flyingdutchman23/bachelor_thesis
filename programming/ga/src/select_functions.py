import random
import numpy as np
from operator import attrgetter

def selRandom(individuals, spb):
    """select k individuals randomly.

    :individuals: the individuals to select from
    :k: the number of individuals to select
    :returns: a tuple of the select individuals and their indices in the given
    individuals

    """

    assert spb <= 1 and spb >= 0
    individual_indices = list(range(len(individuals)))
    chosen_indices = []

    for i in range(len(individuals)):
        if random.random() < spb:
            chosen_idx = random.choice(individual_indices)
            chosen.appen(chosen_idx)
            chosen_indices.remove(chosen_idx)

    chosen = [ individuals[idx] for idx in chosen_indices ]

    return chosen, chosen_indices

def selTournament(individuals, spb, tournsize):
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

    for i in range(len(individuals)):
        if random.random() < spb:
            aspirant_indices = random.sample(individual_indices, tournsize)
            aspirants = [individuals[j] for j in aspirant_indices]
            max_index = aspirants.index(max(aspirants, 
                key=attrgetter("fitness")))
            chosen.append(aspirants[max_index])
            chosen_indices.append(aspirant_indices[max_index])
            individual_indices.remove(aspirant_indices[max_index])

    return chosen, chosen_indices
