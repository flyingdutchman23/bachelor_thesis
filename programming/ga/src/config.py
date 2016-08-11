# to use the system exit function
import sys
#for saving a file with time stamp
import time
# to create a folder
import os
# to copy a file
import shutil
# to round a float number for checking to convert to integer
import math
# to open zipfiles to read RaLaNS data
import zipfile
# to parse config file
import configobj
# to validate config file
from validate import Validator
# to do multiplication
import numpy as np
# to calc borders
import my_util

import io

# contains verious functions to deal with the RaLaNS data
import ralans_helper
# to have the constants
from constants import XAXIS, YAXIS, ZAXIS, DIM, LIST, AREA, CUBIC, POINT,\
        RALANS, PROTOTYPE

CONFIGSPECFILE = "./genetic_algorithm_specifications.cfg"
###Global Constants
DES = None
###Genetic Algorithm constants
#Population Size
POP_SIZE = None
#Number of Generations to run the algorithm
GEN_NUM = None
#Number of Generations after stop when best solution does not improve
UNCHANGED_GEN_NUM = None
# to specify which mutation function should be used
MUTATE = None
# to specify to probability for and individual to be mutated
MUTATE_PROB = None
# to specify to probability for an gen, so a bit, of an individual to be mutated, f.x. the
# probability the a bit in an individual is flipped
MUTATE_IND_PROB = None
# to specify which selection function should be used
SELECT = None
# to specify the arguments given to the selection function
SELECT_ARG = None
# to specify the probability that an individual will be used for the selection.
SELECT_PROB = None
# to specify which reproduction function should be used
MATE = None
# to specify to probability for and individual to be mated
MATE_PROB = None
# to specify which init function should be used
INIT = None
# the argument of the init function, if one is needed for the chosen init function
INIT_ARG = None
# to specify which way to calculate the fitness is used
FITNESS = None
# to specify the number of individuals, which are saved in the hall of fame
HOF_NUM = None
# to specify which replacement function should be used
REPLACE = None
# to specify which arguments replacement function gets
REPLACE_ARG = None
# to specify the weight of the SPNE fitness compared to the number of nodes
WEIGHTS = None

# the positions on the map, which should be evaluated.
POSITIONS = None	
### Data related contants
# type of the data creation, prototype or RaLaNS
TYPE = None
# type of the placement for the prototype, maybe RaLaNS as well
PLACEMENT_TYPE = None
# the borders of the map, these borders + the stepsize compute the length in the
# dimensions
BORDERS = None
# specifies the length in x, y, z direction in a list
LENG = 3 * [None] 
# length of an individual, which is determined by the number of items in a list or by the
# number of rows, columns and layers a area or cubic form has
IND_LEN = None
# for simple version: the maximum distance to communicate, to receive packets
MAX_DIST = None
#for RaLaNS version: the minimum signal strength, so that there can be a connection.
THRESHOLD = None
# the starting height for the cube
COVERAGE_LEVEL = None
# the end height for the cube
COVERAGE_MAX_LEVEL = None 
# the path to the file, which contains the result from RaLANS
FILENAME = None
# the stepsize, which is used in the RaLaNS file
STEPSIZE = None

#so every saved plot in 1 run has same time
START_TIME = time.time()
START_TIME_STR = str(int(START_TIME))

def get_placement_name(placement_type=PLACEMENT_TYPE):
    """returns the name of the type of this placement. It is either 'AREA', 'CUBIC' or
    'LIST'. 

    :placement_type: the number, which describes this placement type.
    :returns: the name of the placement as a string

    """
    if placement_type == AREA:
        return 'AREA'
    elif placement_type == CUBIC:
        return 'CUBIC'
    elif placement_type == LIST:
        return 'LIST'
    else:
        sys.exit(gen_error_message('incorrect PLACEMENT_TYPE: ', placement_type))

def create_result_folder(type_name, placement_name):
    """creates the folder, in which the result files will be placed.

    """
    global FOLDER
    FOLDER = "../results/" + DES + "/"
    FOLDER += type_name + "/"
    FOLDER += placement_name + "/"
    FOLDER += "LEN_" + str(IND_LEN) + "/"

    if "GA" in DES:
        FOLDER += "GEN_NUM_" + str(GEN_NUM) + "/"
        FOLDER += "POP_SIZE_" + str(POP_SIZE) + "/"
        FOLDER += "MUT_" + str(MUTATE) + "_PROB_" + str(MUTATE_PROB) + "/"
        FOLDER += "MATE_" + str(MATE) + "_PROB_" + str(MATE_PROB) + "/"
        FOLDER += "SEL_" + str(SELECT) + "_PROB_" + str(SELECT_PROB) + "/"
        FOLDER += "REP_" + str(REPLACE) + "/"
    FOLDER += "time_" + START_TIME_STR + "/"
    if not os.path.exists(FOLDER):
        os.makedirs(FOLDER)
    else:
        sys.exit(gen_error_message('save folder exists already, \
                it should not! The folder is: ', FOLDER))

def read_header(headerfile):
    """reads the header, the first 2 lines, of the file, which specifies that.

    :headerfile: the path to the file

    """

    global PLACEMENT_TYPE, LENG, STEPSIZE, POSITIONS, IND_LEN, BORDERS
    first_line = headerfile.readline()
    first_line = ralans_helper.conv_byte_to_str(first_line)
    second_line = ralans_helper.conv_byte_to_str(headerfile.readline())
    assert first_line == second_line, \
            "Currently just files with the same receiver \
            and transmitter can be parsed"

    headtr = np.loadtxt(io.StringIO(first_line), delimiter=" ")
    PLACEMENT_TYPE = headtr[0]
    BORDERS, stepsizes, height, length = ralans_helper.parseHead(headtr,
            PLACEMENT_TYPE)
    if PLACEMENT_TYPE == AREA or PLACEMENT_TYPE == CUBIC:
        if TYPE == RALANS:
            assert height[0] == COVERAGE_LEVEL
            assert height[1] == COVERAGE_MAX_LEVEL
        LENG = length

        # set the stepsize according to the PLACEMENT_TYPE
        if PLACEMENT_TYPE == AREA:
            assert stepsizes[0] == stepsizes[1], "unequal stepsizes not supported"
            STEPSIZE = stepsizes[0]
        elif PLACEMENT_TYPE == CUBIC:
            assert stepsizes[0] == stepsizes[1] == stepsizes[2]
            STEPSIZE = stepsizes[0]

        # maybe also good to have for the AREA and CUBIC
        POSITIONS = ralans_helper.parseTransmitterHeader(headtr)

        # if placement type is cubic or area, then the lenght of an individual
        # is just the multiplicaion of the length in each axis

        IND_LEN = np.prod(LENG)
        # print('LENG: ', LENG)
        # print('IND_LEN: ', IND_LEN)
        # print('len(POSITIONS): ', len(POSITIONS))
        assert IND_LEN == len(POSITIONS)

    elif PLACEMENT_TYPE == LIST:
        if math.floor(length) == int(length):
            IND_LEN = int(length)
        else:
            sys.exit(gen_error_message('error for IND_LEN cast to int: ', IND_LEN))
        POSITIONS = ralans_helper.parseTransmitterHeader(headtr)
        assert IND_LEN == len(POSITIONS)
        LENG[XAXIS] = len(POSITIONS)
        LENG[YAXIS] = 1
        LENG[ZAXIS] = 1
        if TYPE == PROTOTYPE:
            data_borders = my_util.calc_borders(POSITIONS)
            data_borders = my_util.remove_border_axis(data_borders)
            BORDERS = data_borders

    headerfile.close()

def fill_config(configfile):
    """
    fill the config global variables with the values given by the config argument. Quits,
    if something is invalid.

    :config: contains the arguments given from the parser of argparse.
    :returns: None

    """

    configspec = configobj.ConfigObj(CONFIGSPECFILE, list_values=False)
    config = configobj.ConfigObj(configfile, configspec=configspec, list_values=True)
    val = Validator()
    test_passed = config.validate(val)
    if not test_passed:
        sys.exit(gen_error_message('Validation incorrect!!!', test_passed))
    
    #read the description, relevant for the saving path
    global DES
    DES = config['DES']

    genetic_arg_options = ['MUTATE', 'SELECT', 'REPLACE', 'MATE', 'INIT', 
            'FITNESS']
    genetic_args = list(genetic_arg_options)
    genetic_args.extend(['POP_SIZE','GEN_NUM', 'UNCHANGED_GEN_NUM', 
        'MUTATE_IND_PROB','SELECT_PROB', 'MUTATE_PROB','INIT_ARG','HOF_NUM',
        'WEIGHTS', 'SELECT_ARG', 'REPLACE_ARG', 'MATE_PROB'])

    for argument_name in genetic_args:
        globals()[argument_name] = config['genetic_algorithm'][argument_name]
    for argument_name in genetic_arg_options:
        globals()[argument_name] = int(globals()[argument_name])

    # convert the list into a tuple of float to be compatible with DEAP
    global WEIGHTS
    WEIGHTS = [float(weight) for weight in WEIGHTS]
    WEIGHTS = tuple(WEIGHTS)

    global TYPE, MAX_DIST, BORDERS, PLACEMENT_TYPE, STEPSIZE
    global COVERAGE_LEVEL, COVERAGE_MAX_LEVEL, LENG, POSITIONS, IND_LEN
    global FILENAME, THRESHOLD

    TYPE = int(config['data']['TYPE'])

    if TYPE == PROTOTYPE:
        TYPE_NAME = 'prototype'
        FILENAME = config['data']['prototype']['FILENAME']
        MAX_DIST = config['data']['prototype']['MAX_DIST']
        resfile = open(FILENAME)
        read_header(resfile)

    elif TYPE == RALANS:
        TYPE_NAME = 'ralans'
        FILENAME = config['data']['ralans']['FILENAME']
        THRESHOLD = config['data']['ralans']['THRESHOLD']

        resfile, ralans_configfile, _ = ralans_helper.getFiles(FILENAME)

        ralans_config = ralans_helper.parseConfigFile(ralans_configfile, isZip=True)
        STEPSIZE = ralans_config['stepSize']
        COVERAGE_LEVEL = ralans_config['coverageLevel']
        COVERAGE_MAX_LEVEL = ralans_config['coverageMaxLevel']
        MAX_DIST = ralans_config['maxRange']

        # to read the header of the result RaLaNS file
        read_header(resfile)

    else:
        sys.exit(gen_error_message('error for TYPE', TYPE))

    assert len(LENG) == 3
    create_result_folder(TYPE_NAME, get_placement_name(PLACEMENT_TYPE))


    # save the config of RaLaNS
    if TYPE == RALANS:
        zf = zipfile.ZipFile(FILENAME,'r')
        zf.extract('config.cfg',FOLDER)
        ralans_configfile.close()

        # for pos in POSITIONS:
            # print("Boders: ", BORDERS)
            # print("pos: ", pos)
            # assert pos[XAXIS] >= BORDERS[0]
            # assert pos[YAXIS] >= BORDERS[1]
            # assert pos[XAXIS] <= BORDERS[2]
            # assert pos[YAXIS] <= BORDERS[3]



    # save a copy of the configfile in the result folder as well
    shutil.copyfile(configfile, FOLDER+'genetic_algorithm.cfg')

    print(BORDERS)
    assert len(BORDERS) == 4

    print('FILENAME: ', FILENAME)
    print('LENG: ', LENG)
    print('FOLDER: ', FOLDER)

def gen_error_message(message, arg):
    """generates an error message for the invalid argument with its value and type

    :message: the text, which should be added to the value and type
    :arg: the argument, which causes the error
    :returns: the full error message

    """
    message += '\n'
    message += 'the value is: ' + str(arg)
    message += '\n'
    message += 'the type is: ' + str(type(arg))

    return message
