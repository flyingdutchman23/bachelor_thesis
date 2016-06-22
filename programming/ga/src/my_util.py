### all kind of small functions needed for this project

import numpy as np
import copy

DIM = 3
XAXIS = 0
YAXIS = 1
ZAXIS = 2
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
