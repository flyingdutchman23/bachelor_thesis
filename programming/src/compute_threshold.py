import scipy
import itertools
import argparse
import numpy as np

import config
import ralans_wrapper as ralans
import ralans_helper
import spne
import plot_helper
import init_functions as init

def compute_threshold_by_pos(pos1, pos2):
    """shows the signal strength between 2 positions by their closest match for
    RALANS

    :pos1: the 1st position 
    :pos2: the 2nd position 
    :returns: the signal strength

    """
    ind1 = ralans_helper.get_nextid_by_pos(pos1, config.POSITIONS)
    ind2 = ralans_helper.get_nextid_by_pos(pos2, config.POSITIONS)
    return compute_threshold(ind1, ind2)


def compute_threshold(ind1, ind2):
    """shows the signal strength between 2 indices for RALANS

    :ind1: the 1st index
    :ind2: the 2nd index
    :returns: the signal strength

    """
    
    individual = init.zeros()
    individual[ind1] = 1
    individual[ind2] = 1
    
    pos1 = config.POSITIONS[ind1]
    pos2 = config.POSITIONS[ind2]
    dist = np.linalg.norm(np.subtract(pos1,pos2))
    signal1 = ralans.get_signal(ind1,ind2)
    signal2 = ralans.get_signal(ind2,ind1)

    print("real Position 1: ", pos1)
    print("real Position 2: ", pos2)
    print('Distance: ', dist)
    print('Signal 1: ', signal1)
    print('Signal 2: ', signal2)

    plot_helper.scatter_map_dist(individual, "nodes_positions",
            print_fitness=False)

    return signal1, signal2

def main():

    # positions used for areas, changed a bit for each instance
    # pos1 = [258,313,1]
    # pos2 = [438,493,1]
    # pos1 = [8,-377,1]
    # pos2 = [263,-377,1]
    # pos1 = [8,-407,1]
    # pos2 = [263,-407,1]

    # positions used for sedanplatz_streets
    pos1 = [-30,530,1]
    pos2 = [195,350,1]

    print("given Position 1: ", pos1)
    print("given Position 2: ", pos2)

    configfile = "/home/joris/workspace/bachelor_thesis/programming/ga/configfiles/ga_new.cfg"
    config.fill_config(configfile)
    print("after fill config")
    ralans.init()

    signal = compute_threshold_by_pos(pos1, pos2)

if __name__ == "__main__":
    main()
