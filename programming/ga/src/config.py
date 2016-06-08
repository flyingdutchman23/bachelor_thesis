# to use the system exit function
import sys
#for saving a file with time stamp
import time
# to create a folder
import os
# to copy a file
import shutil
# to parse the RaLaNS config
from port3_ralans.viewer2d import getFiles, parseConfigFile, parseResFile
# to open zipfiles to read RaLaNS data
import zipfile
# to parse config file
import configobj
# to validate config file
from validate import Validator
# to do multiplication
import numpy as np

CONFIGSPECFILE = "./genetic_algorithm_specifications.cfg"
###Global Constants
###Genetic Algorithm constants
#Population Size
POP_SIZE = None
#Number of Generations to run the algorithm
GEN_NUM = None
# to specify which mutation function should be used
MUTATE = None
# to specify to probability for and individual to be mutated
MUTATE_PROB = None
# to specify to probability for an gen, so a bit, of an individual to be mutated, f.x. the
# probability the a bit in an individual is flipped
MUTATE_IND_PROB = None
# to specify which selection function should be used
SELECTION = None
# to specify which reproduction function should be used
MATE = None
# to specify which init function should be used
INIT = None
# the argument of the init function, if one is needed for the chosen init function
INIT_ARG = None
# to specify which way to calculate the fitness is used
FITNESS = None
# to specify the number of individuals, which are saved in the hall of fame
HOF_NUM = None

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
# the stepsize, which is used between the borders and between the height for the
# area and the cubic types
STEPSIZE = None
# specifies the length in x, y, z direction in a list
LENG = 3 * [None] 
# length of an individual, which is determined by the number of items in a list or by the
# number of rows, columns and layers a area or cubic form has
IND_LEN = None
# for simple version: the maximum distance to communicate, to receive packets
MAX_DIST = None
#for simple version: the real distance between each cell of the matrix
REAL_DIST_CELL = None
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

# the constant for area
AREA = 2
# the constant for cubic
CUBIC = 3
# the constant for list
LIST = 4

#so every saved plot in 1 run has same time
START_TIME = time.time()
START_TIME_STR = str(int(START_TIME))

#to save plots in that folder
FOLDER = "../results/" + "ga_run_" + START_TIME_STR + "/"
if not os.path.exists(FOLDER):
    os.makedirs(FOLDER)
else:
    sys.exit('save folder exists already, it should not!')

def fill_config(configfile):
    """
    fill the config global variables with the values given by the config argument. Quits,
    if something is invalid.

    :config: contains the arguments given from the parser of argparse.
    :returns: None

    """

    # save a copy of the configfile in the result folder as well
    shutil.copyfile(configfile, FOLDER+'genetic_algorithm.cfg')

    configspec = configobj.ConfigObj(CONFIGSPECFILE, list_values=False)
    config = configobj.ConfigObj(configfile, configspec=configspec, list_values=True)
    val = Validator()
    test = config.validate(val)
    if test == True:
            print('Succeeded.')
    else:
        sys.exit(gen_error_message('Validation incorrect!!!', test))
    
    genetic_arg_options = ['MUTATE', 'SELECT', 'MATE', 'INIT', 'FITNESS']
    genetic_args = list(genetic_arg_options)
    genetic_args.extend(['POP_SIZE','GEN_NUM','MUTATE_IND_PROB',
        'MUTATE_PROB','INIT_ARG','HOF_NUM'])

    for argument_name in genetic_args:
        globals()[argument_name] = config['genetic_algorithm'][argument_name]
    for argument_name in genetic_arg_options:
        globals()[argument_name] = int(globals()[argument_name])


    global TYPE, MAX_DIST, BORDERS, REAL_DIST_CELL, PLACEMENT_TYPE, STEPSIZE
    global COVERAGE_LEVEL, COVERAGE_MAX_LEVEL, LENG, POSITIONS, IND_LEN
    TYPE = int(config['data']['TYPE'])
    print('type init: ',type(INIT))

    if TYPE == 0:
        MAX_DIST = config['data']['prototype']['MAX_DIST']
        BORDERS = config['data']['prototype']['BORDERS']
        print('borders',BORDERS)
        BORDERS = [int(i) for i in BORDERS]
        REAL_DIST_CELL = config['data']['prototype']['REAL_DIST_CELL']
        PLACEMENT_TYPE = int(config['data']['prototype']['PLACEMENT_TYPE'])
        STEPSIZE = config['data']['prototype']['STEPSIZE']   

        if PLACEMENT_TYPE == CUBIC:
            COVERAGE_LEVEL = config['data']['prototype']['cubic']['COVERAGE_LEVEL']   
            COVERAGE_MAX_LEVEL = config['data']['prototype']['cubic']['COVERAGE_MAX_LEVEL']   
            LENG[2] = COVERAGE_MAX_LEVEL - COVERAGE_LEVEL
        elif PLACEMENT_TYPE == LIST:
            POSITIONS = config['data']['prototype']['list']['POSITIONS']   
        elif PLACEMENT_TYPE == AREA:
            LENG[0] = BORDERS[2] - BORDERS[0]
            LENG[1] = BORDERS[3] - BORDERS[1]
            LENG[2] = 1
        else:
            sys.exit('PLACEMENT_TYPE not available')

        # set the length of an individual
        if PLACEMENT_TYPE == LIST:
            IND_LEN = len(POSITIONS)
        else:
            IND_LEN = np.prod(LENG)
            print('IND_LEN in config: ',IND_LEN)

    elif TYPE == 1:
        FILENAME = config['data']['ralans']['FILENAME']
        resfile, bdfile, ralans_configfile = getFiles(FILENAME)
        ralans_config = parseConfigFile(ralans_configfile, isZip=True)
        STEPSIZE = ralans_config['stepSize']
        COVERAGE_LEVEL = ralans_config['coverageLevel']
        COVERAGE_MAX_LEVEL = ralans_config['coverageMaxLevel']
        MAX_DIST = ralans_config['maxRange']
    else:
        sys.exit(gen_error_message('error for TYPE', TYPE))


    assert len(BORDERS) == 4
    # TODO calculates the number of rows and columns

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
