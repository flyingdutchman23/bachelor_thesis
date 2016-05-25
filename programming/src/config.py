
###Global Constants

#Population Size
POP_SIZE = 40
#Number of Generations to run the algorithm
GEN_NUMBER = 40


#Number of rows the map has
ROWS = 13
#Number of columns the map has
COLS = 13
#length of an individual
IND_LEN = ROWS * COLS

#for simple version: the maximum distance to communicate, to receive packets
MAX_DIST = 3.3
#for simple version: the real distance between each cell of the matrix
REAL_DIST_CELL = 1

###Settings for RaLaNS
#for RaLaNS version: the minimum signal strength, so that there can be a connection.
THRESHOLD = -100
#The heigth of the grid on the map
HEIGHT = 1
# the path to the file, which contains the result from RaLANS
FILENAME = "/home/joris/workspace/RaLaNS_data/small_street_flat_cover.zip"
# the stepsize, which is used in the RaLaNS file
STEPSIZE = 1
