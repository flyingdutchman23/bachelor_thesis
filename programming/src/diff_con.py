import config
import ralans_wrapper as ralans
import init_functions as init
import plot_helper

def compute_diff():
    
    ind = init.zeros()
    max_diff = 0
    max_signal1 = None
    max_signal2 = None
    max_pos1 = None
    max_pos2 = None

    for i in range(len(ind)):
        print('i: ', i)
        for j in range(i+1, len(ind)):
            signal1 = ralans.get_signal(i,j)
            signal2 = ralans.get_signal(j,i)

            diff = abs(signal1 - signal2)
            if diff > max_diff:
                max_diff = diff
                max_signal1 = signal1
                max_signal2 = signal2
                max_pos1 = i
                max_pos2 = j

    print('max diff: ', max_diff)
    print('max signal1: ', max_signal1)
    print('max signal2: ', max_signal2)

    individual = init.zeros()
    individual[max_pos1] = 1
    individual[max_pos2] = 1

    plot_helper.scatter_map_dist(individual, "nodes_positions",
            print_fitness=False)

def main():

    configfile = "/home/joris/workspace/bachelor_thesis/programming/ga/configfiles/ga_new.cfg"
    config.fill_config(configfile)
    print("after fill config")
    ralans.init()

    compute_diff()

if __name__ == "__main__":
    main()
