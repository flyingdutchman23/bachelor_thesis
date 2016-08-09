import numpy as np
import os
# to parse config file
import configobj
import argparse

import ralans_wrapper as ralans
import plot_helper
import init_functions as init
import my_util
from os.path import expanduser

parser = argparse.ArgumentParser(
    description='Start the genetic algorithm with the given config file.')
parser.add_argument('configfile', metavar='C', type=str,
                            help='the path to the config file')

def main():

    home = expanduser("~")
    save_folder = home + "/" + "Desktop/"

    # configfile = "/home/joris/workspace/bachelor_thesis/programming/ga/configfiles/evaluate_mut.cfg"
    args = parser.parse_args()
    config = configobj.ConfigObj(args.configfile, list_values=True)
    name = config['name']
    descs = config['descs']
    descs = [ desc.replace('qq', '\n') for desc in descs]
    var_folds = config['var_folds']
    base_fold = config['base_fold']
    aft_var_fold = config['aft_var_fold']
    title = config['title']
    plot_type = config['type']
    max_evals = int(config['max_evals'])
    print(descs)
    assert len(descs) == len(var_folds)
    selects = [config['select']] * len(descs)

    logbook_folds = []
    for i in range(len(var_folds)):
        fold = base_fold + var_folds[i] + aft_var_fold
        times = os.listdir(fold)
        assert len(times) >= 1
        print('times 0: ', times[0])
        fold += times[0]
        logbook_folds.append(fold)

    logbooks = []
    for fold in logbook_folds:
        logbooks.append(my_util.load_logbook(fold+"/logbook.ser"))
        

    if plot_type == 'normal':
        plot_helper.combine_plots(logbooks, selects, descs, save_folder,
                name=name, title=title)
    elif plot_type == 'bar':
        plot_helper.bar_plot(logbooks, selects, descs, save_folder,
                name=name, title=title, max_evals=max_evals)

if __name__ == "__main__":
    main()
