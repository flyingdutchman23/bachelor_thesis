import scipy
import itertools
import argparse
import numpy as np

import config
import ralans_wrapper as ralans
import spne
import plot_helper

parser = argparse.ArgumentParser(
    description="""Start the brute force calculation on the specified configfile
    with a given number of nodes to place for each solution. This script
    calculates the global optimum by iterating over all possible solutions.""")
parser.add_argument('configfile', metavar='C', type=str,
                            help='the path to the config file')
parser.add_argument('num_of_nodes', metavar='N', type=int,
                            help='the number of nodes to place')

def brutforce(num_of_nodes, ind_len=config.IND_LEN):
    """TODO: computes the global optima by iterating over all solutions.

    :num_of_nodes: the number of nodes in each solution
    :ind_len: the number of possible positions the nodes can be placed. That has
    to be the length of the individual, which is definded by the data of RalaNS.
    :returns: a tuple of the best fitness and best solution

    """
    
    assert ind_len is not None
    assert ind_len > 0

    fitness_max = 0
    individual_max = None

    for node_poss in itertools.combinations(range(ind_len),num_of_nodes):
        print('Node positions: ', node_poss)
        individual = np.zeros(ind_len)
        for node_pos in node_poss:
            individual[node_pos] = 1

        fitness = spne.graph_evaluate(individual)[0]
        if fitness > fitness_max:
            fitness_max = fitness
            individual_max = individual

    return fitness_max, individual_max

def main():
    args = parser.parse_args()
    config.fill_config(args.configfile)
    print("after fill config")
    ralans.init()
    f_max, ind_max = brutforce(args.num_of_nodes, ind_len=config.IND_LEN)

    print('Maximum Fitness: ', f_max)
    print('Maximum Individual: ', ind_max)

    plot_helper.draw_individual_graph(ind_max, "brutforce_best_graph")
    plot_helper.scatter_map_dist(ind_max, "global_optima")

    my_util.save_node_positions(config.FOLDER+"transmitterposs.txt", ind_max,
            config.POSITIONS)
    
if __name__ == "__main__":
    main()
