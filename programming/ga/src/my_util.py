#all kind of small functions needed for this project
import config

def onedpos_to_2dpos(pos):
    """converts the position of the array into a tuple, which describes the position in
    the grid with a value for the row and a value for the column.

    :pos: the position in the array, has to be an integer
    :returns: the position as a 2d tuple: (row,column)

    """

    pos_row = int(pos / config.LENG[0])
    pos_col = pos % config.LENG[0]

    return [pos_row, pos_col]
