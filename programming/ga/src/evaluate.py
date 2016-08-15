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
    yaxis = config['yaxis']
    xaxis = config['xaxis']
    plot_type = config['type']
    max_evals = int(config['max_evals'])
    comp_by_evals = int(config['comp_by_evals'])
    comp_by_gens = int(config['comp_by_gens'])
    col = int(config['col'])
    print(descs)
    assert len(descs) == len(var_folds)
    selects = [config['select']] * len(descs)

    logbooks_folds = []
    for i in range(len(var_folds)):
        logbooks_folds.append([])
        fold = base_fold + var_folds[i] + aft_var_fold
        times = os.listdir(fold)
        assert len(times) >= 1
        for time in times:
            logbooks_folds[i].append(fold+time)

    logbooks = []
    logbookss = []
    for i in range(len(logbooks_folds)):
        logbookss.append([])
        logbook_folds = logbooks_folds[i]
        print(logbook_folds)
        logbooks.append(my_util.load_logbook(logbook_folds[0]+"/logbook.ser"))
        for fold in logbook_folds:
            logbookss[i].append(my_util.load_logbook(fold+"/logbook.ser"))

        

    if plot_type == 'normal':
        plot_helper.combine_plots(logbooks, selects, descs, save_folder,
                name=name, title=title)
    elif plot_type == 'norm_one_fold':
        assert len(logbookss) == 1
        logbooks = logbookss[0]
        assert len(logbooks) > 1
        assert len(selects) == 1
        assert len(descs) == 1
        selects = selects * len(logbooks)
        descs = descs * len(logbooks)
        plot_helper.combine_plots(logbooks, selects, descs, save_folder,
                name=name, title=title, yaxis=yaxis, xaxis=xaxis)
    elif plot_type == 'bar':
        plot_helper.bar_plot(logbooks, selects, descs, save_folder,
                name=name, title=title, max_evals=max_evals)
    elif plot_type == 'box':
        plot_helper.box_plot(logbookss, selects, descs, save_folder,
                name=name, title=title, max_evals=max_evals, 
                comp_by_evals=comp_by_evals, col=col, yaxis=yaxis,
                comp_by_gens=comp_by_gens, xaxis=xaxis)

if __name__ == "__main__":
    main()
