#File to keep some mutate functions

import config

import numpy as np

import random

def lochert_mutate_one(individual):
    """mutates an individual such that a 0 value is flipped to 1 and another 1 value
    flipped to zero. Wich bits will be flipped is choosen randomly.

    asserts that there is at least 1 node in the individual
    asserts that the number of nodes is smaller than the length of individual. That means
    there has to be at least cell, which does not contain a node.

    :individual: the given individual
    :returns: the modified, mutated individual as a tuple with 1 element

    """

    #flip a 1 to a 0
    nonzeros = np.nonzero(individual)[0]
    flip_pos = random.choice(nonzeros)
    individual[flip_pos] = 0

    #flip a 0 to a 1
    zeros = np.delete(np.arange(config.IND_LEN),nonzeros)
    flip_pos = random.choice(zeros)
    individual[flip_pos] = 1

    return individual,   

def lochert_mutate_flexible(individual, indp):
    """mutates an individual such that a 1 value with the given probability is flipped to 
    0 and another 0 value flipped to 1. All 1 values will be flipped with the given
    probability.

    :individual: the given individual
    :indp: the probability with which each node and a randomly choosen other position is
    flipped
    :returns: the modified, mutated individual

    """
    #TODO implement the function
    pass
