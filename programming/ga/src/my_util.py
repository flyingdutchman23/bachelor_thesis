### all kind of small functions needed for this project
import array
import numpy as np
import copy
import pickle

#from the genetic algorithms package to load the dictionary
from deap import creator
from deap import base

# to have the constants available
from constants import DIM, XAXIS, YAXIS, ZAXIS

def onedpos_to_2dpos(pos, positions):
    """converts the position of the array into a tuple, which describes the position in
    the grid with a value for the row and a value for the column.

    :pos: the position in the array, has to be an integer
    :returns: the position as a 2d tuple: (row,column)

    """

    pos = positions[pos]

    assert len(pos) == DIM
    pos = pos[:2]

    return pos

def calc_borders(positions):
    borders = [None] * 6

    positions = np.array(positions)
    mins = np.amin(positions, axis=0)
    assert len(mins) == 3, 'Mins: ' + str(mins)

    borders[:3] = mins[:]

    maxs = np.amax(positions, axis=0)
    assert len(maxs) == 3

    borders[3:] = maxs[:]

    return borders

def isin_borders(bigger_borders, smaller_borders):
    """checks whether the smaller area specified by the smaller borders is in the area
    specified by the bigger borders.

    :bigger_borders: TODO
    :smaller_borders: TODO
    :returns: true, if smaller is in bigger. False, else.

    """
    assert len(bigger_borders) == len(smaller_borders)
    assert len(bigger_borders) % 2 == 0
    assert len(bigger_borders) <= 6

    isin = np.array([None] * len(bigger_borders))
    isin[:3] = bigger_borders[:3] <= smaller_borders[:3]
    isin[3:] = bigger_borders[3:] >= smaller_borders[3:]

    return all(isin)

def remove_border_axis(borders, axis=ZAXIS, dim=DIM):
    """removes the border for a particular given axis. So the result will contain the same
    elements in the same order - the border elements for the given axis

    :borders: TODO
    :returns: TODO

    """

    borders = copy.deepcopy(borders)
    del borders[dim + axis]
    del borders[axis]

    return borders

def calc_size(borders):
    """calculates the size for each axis specified by the given borders. The borders
    should be either just contain the values for the x and y dimension or for the x, y and
    z dimension.

    :borders: the borders values for the data
    :returns: the size of the data(map) in each dimension

    """
    assert len(borders) % 2 == 0
    assert len(borders) <= 2*DIM
    size = [None] * len(borders)
    for i in range(len(size)):
        size[i] = borders[len(size) + i] - borders[i]

    return size

def save_node_positions(filepath, individual, positions):
    """save the positions of the nodes to a txt file.

    :filepath: TODO
    :individual: TODO
    :POSITIONS: TODO
    :returns: TODO

    """
    output = open(filepath, "w")

    for index, gen in enumerate(individual):
        if gen==1:
            line = "Pos: " + str(positions[index]) + "\n"
            output.write(line)

    output.close()

def save_ind_txt(filepath, ind):
    """save an individual to a txt file

    """
    output = open(filepath, "w")

    for i in ind:
        output.write(str(i))

    output.write("\n")

    output.close()

def save_ind(filepath, ind):
    """save an individual to a txt file

    """
    output = open(filepath, "wb")

    pickle.dump(ind, output)

    output.close()

def load_ind(filepath, weights=(1.0,)):
    """save an individual to a txt file

    """
    input_ind = open(filepath, "rb")

    creator.create("MYFIT", base.Fitness, weights=weights)
    creator.create("Individual", array.array, typecode='b',
            fitness=creator.FitnessMax)

    ind = pickle.load(input_ind)
    output.close()

    return ind

def save_logbook(filepath, log):
    """save the logbook

    """
    output = open(filepath,'wb')
    pickle.dump(log, output)
    output.close()

def load_logbook(filepath):

    input_log = open(filepath,'rb')
    logbook = pickle.load(input_log)
    return log

def save_dict(filepath, dictionary):
    """save a dictionary object to a file for persistence.

    :filepath: the path of the file
    :dict: the dictionary

    """
    output = open(filepath,'wb')
    pickle.dump(dictionary, output)
    output.close()

def load_dict(filepath, weights=(1.0,)):
    """load a dictionary, which was saved with save_dict before from a specified
    file.

    :filepath: the path to the file
    :returns: the dictionary object

    """

    creator.create("MYFIT", base.Fitness, weights=weights)
    creator.create("Individual", array.array, typecode='b',
            fitness=creator.FitnessMax)

    input_dict = open(filepath, 'rb')
    dictionary = pickle.load(input_dict)
    input_dict.close()

    assert isinstance(dictionary, dict)

    return dictionary

def frange(x, y, jump):
    while x <= y:
        yield x
        x += jump
