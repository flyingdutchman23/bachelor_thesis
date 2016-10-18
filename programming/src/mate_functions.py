#This file will contain different mate functions

#to initialize an individual
import array

#to initialize an individual with just 0s
import init_functions as init

import numpy as np

import random

import config

import print_helper

def lochert_mate(ind1,ind2):
    """calculates the child of the mating process done by the 2 given individual. It 
    generates just 1 child.

    the number of nodes in the 2 individuals should be the same, but it will work with
    different number of nodes. It will use the number of nodes of the first given
    individual. 

    :ind1: the 1st individual for the mating process

    :ind2: the 2nd individual for the mating process

    :returns: a tuple with the child on position 0 and the second individual on position 1

    """
    
    # the need to have the same length, because the number of nodes should be
    # fixed, when using this function
    assert sum(ind1) == sum(ind2)

    remaining_nodes = []
    # to count the total number of nodes 
    count_total = 0
    # to count the number of nodes set in the child
    count_set = 0
    
    for i in range(len(ind1)):
        count_total += ind1[i] + ind2[i]
        if ind1[i] != ind2[i]:
            remaining_nodes.append(i)
        ind1[i] = ind1[i] and ind2[i]
        ind2[i] = ind1[i]
        count_set += ind1[i]

    remain_num = int(count_total/2 - count_set)
    add1 = random.sample(remaining_nodes,remain_num)
    add2 = random.sample(remaining_nodes,remain_num)

    for node in add1:
        ind1[node] = 1

    for node in add2:
        ind2[node] = 1

    return ind1, ind2
