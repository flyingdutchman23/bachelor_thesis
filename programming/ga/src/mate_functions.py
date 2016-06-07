#This file will contain different mate functions

#to initialize an individual
import array

#to initialize an individual with just 0s
import init_functions as init

import numpy as np

import random

import config

import print_helper

#TODO add mate function from Lochert2008c, which keeps the number of nodes equal
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
    
    # the need to have the same length, because the number of nodes should be fixed, when
    # using this function
    # assert sum(ind1) == sum(ind2)

    # print("Before MATE !!!!")
    # print_helper.individual(ind1)
    # print_helper.individual(ind2)

    remaining_nodes = []
    # to count the total number of nodes 
    count_total = 0
    # to count the number of nodes set in the child
    count_set = 0
    
    for index in range(config.IND_LEN):
        if ind1[index] ==  1:
            count_total += 1
            if ind2[index] == 1:
                ind1[index] = 1
                count_set += 1
            else:
                remaining_nodes.append(index)
                ind1[index] = 0
        elif ind2[index] == 1:
            remaining_nodes.append(index)
            ind1[index] = 0
        else:
            ind1[index] = 0

    remaining_nodes = random.sample(remaining_nodes,count_total - count_set)

    for node in remaining_nodes:
        ind1[node] = 1

    # print()
    # print("After MATE !!!!")
    # print_helper.individual(ind1)
    # print_helper.individual(ind2)
    # print("sum individual 1:",sum(ind1))
    # print("sum individual 2:",sum(ind2))

    return ind1, ind2
