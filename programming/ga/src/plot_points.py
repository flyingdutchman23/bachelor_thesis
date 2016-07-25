import numpy as np

import config
import ralans_wrapper as ralans
import plot_helper
import init_functions as init

def main():

    configfile = "/home/joris/workspace/bachelor_thesis/programming/ga/configfiles/ga_new.cfg"
    config.fill_config(configfile)
    print("after fill config")

    ralans.init()
    individual = init.ones()
    plot_helper.scatter_map_dist(individual, "nodes_positions",
            print_fitness=False)

if __name__ == "__main__":
    main()
