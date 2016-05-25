
########################################################################################################################
# Copyright (c) 2015, University of Osnabrueck                                                                         #
#   All rights reserved.                                                                                               #
#                                                                                                                      #
#   Redistribution and use in source and binary forms, with or without modification, are permitted provided that the   #
#   following conditions are met:                                                                                      #
#                                                                                                                      #
#   1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following#
#       disclaimer.                                                                                                    #
#                                                                                                                      #
#   2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the       #
#       following disclaimer in the documentation and/or other materials provided with the distribution.               #
#                                                                                                                      #
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, #
#   INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE  #
#   DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, #
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR    #
#   SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,  #
#   WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE   #
#   USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.                                           #
########################################################################################################################

import os

#you can change the forder structure and filenames here, not recommended, there has to be some adjustments in the c++ code too, marked with !
fInputfiles  = 'inputfiles/'
fOutputfiles = 'outputfiles/'
fConfigfiles = 'configfiles/'
fViewerConfig= 'viewerconfig/'
fPolygons    = 'polygons/'      # !
fEdges       = 'edges/'         # !
fRays        = 'rays/'          # !
fLogs        = 'logs/'          # !
fCoverage    = 'coverage/'      # !
fTmp         = 'tmp/'           # !

logScript    = 'script.log'
logLauncher  = 'launcher.log'   # !
logEdge      = 'edge.log'       # !
fileBuildings= 'buildings.txt'  # !
fileEdges    = 'edges.txt'      # !
fileTerrain  = 'terrain.txt'    # !
fileStreets  = 'streets.txt'    # !
binBuildings = 'buildings.bin'
binTerrain   = 'terrain.bin'

cppFiles = 'src/launcher/'
cppEdge = 'edges'
cppLauncher = 'launcher'

# cluster default values
clusterEdgeName = 'RaLaNSextEdges'
clusterEdgeMem = '1gb'
clusterEdgeMsg = 'bea'
clusterLauncherName= 'RaLaNSLauncher'
clusterLauncherMem = '2gb'
clusterLauncherMsg = 'a'
clusterCollectName= 'RaLaNScollect'
clusterCollectMem = '1gb'
clusterCollectMsg = 'ea'


def createTorqueCommand(dict, name='RaLaNS', cores='select=1:ncpus=1', mem='2100mb', wtime='168:00:00', msg='a', array=None):
    nl = "\n"

    cmd  = "#PBS -N \"" + (dict['clusterName'] if 'clusterName' in dict and dict['clusterName'] is not None else name) + "\"" + nl
    cmd += '#PBS -j oe' + nl    #print error and output in one file
    if 'clusterMail' in dict and dict['clusterMail'] is not None:
        cmd += '#PBS -M ' + dict['clusterMail'] + nl
        cmd += '#PBS -m ' + (dict['clusterMsg'] if 'clusterMsg' in dict and dict['clusterMsg'] is not None else msg) + nl
    cmd += "#PBS -l " + (dict['clusterCores'] if 'clusterCores' in dict and dict['clusterCores'] is not None else cores) + ':mem=' + (dict["clusterMem"] if 'clusterMem' in dict and dict['clusterMem'] is not None else mem)
    cmd += ",walltime=" + (dict['clusterWtime'] if 'clusterWtime' in dict and dict['clusterWtime'] is not None else wtime) + nl

    if array is not None:
        array = dict['clusterArray'] if 'clusterArray' in dict and dict['clusterArray'] is not None else array
        if "_" in array:
            split = array.split("_")
            array = split[0] + "-" + split[1]
        cmd += '#PBS -t ' + array
        if dict['clusterLimit'] is not None:
            cmd += "%" + str(dict['clusterLimit'])
        cmd += nl

    cmd += 'cd $PBS_O_WORKDIR \n'
    return cmd


def createPBSProCommand(dict, name='RaLaNS', cores='select=1:ncpus=1', mem='2100mb', wtime='48:00:00', msg='a', array=None):
    nl = "\n"

    cmd = "#!/bin/bash\n"
    cmd += '#PBS -N "' + (dict['clusterName'] if 'clusterName' in dict and dict['clusterName'] is not None else name) + '"' + nl
    cmd += '#PBS -j oe' + nl    #print error and output in one file
    if 'clusterMail' in dict and dict['clusterMail'] is not None:
        cmd += '#PBS -M ' + dict['clusterMail'] + nl
        cmd += '#PBS -m ' + (dict['clusterMsg'] if 'clusterMsg' in dict and dict['clusterMsg'] is not None else msg) + nl
    cmd += '#PBS -l ' + (dict['clusterCores'] if 'clusterCores' in dict and dict['clusterCores'] is not None else cores) + ':mem=' + (dict["clusterMem"] if 'clusterMem' in dict and dict['clusterMem'] is not None else mem)
    cmd += ",walltime=" + (dict['clusterWtime'] if 'clusterWtime' in dict and dict['clusterWtime'] is not None else wtime) + nl

    if array is not None:
        array = dict['clusterArray'] if 'clusterArray' in dict and dict['clusterArray'] is not None else array
        if "_" in array:
            split = array.split("_")
            array = split[0] + "-" + split[1]
        x,y = array.split("-")
        if x == y:      #workaround, because arrays with 1 element are not supported
            array = x + "-" + str(int(y.split(":")[0])+1) + ":2"
        cmd += '#PBS -J ' + array  + '\n'

    cmd += 'cd $PBS_O_WORKDIR \n'
    return cmd


#Constant Values for debugging
LOG1 = 1
LOG2 = 2
LOG3 = 3
LOGFULL = 4
DEV = 5

#Default configuration for RaLaNS
config = {
    "borders":              [],     # [-51, -27, 53, 21] usually the borders are determined from data, you can limit the coverage area manually here
    "buildingHeight":       10,     # used for osm maps, sets the height of each building
    "calculationServers":   (),     # you can distribute calculations to other computers, which are running calculationServer.py (only used if u have more transmitters than 'numberWorkers'), "('ip1','ip2',...)"
    "center":               None,   # [433663.812, 5793036.36, 0]usually the center is determined from data and used as origin, you can choose a center manually here
    "cluster":              False,  # set to True for internal clusterUsage, You can edit the default settings above or set commands for all three jobs in the following lines | it is recommended to run the script with only -m as param before and set the generated zipfile as inputfile
    "clusterArray":         None,   # set ArrayIndices to calculated transmitter with ids in the given range, format: X_Y | X,Y start and end indices
    "clusterCores":         None,   # has to be this syntax: select=X:ncpus=Y | where X is the amount of nodes and Y is the amount of cores. Usally you dont have to change the default settings: select=1:ncpus=1
    "clusterLimit":         None,   # set the amount of parallel calculation at once on cluster, only working on inf-cluster
    "clusterMail":          None,   # your email-address
    "clusterMem":           None,   # set the amount of memory your scripts use
    "clusterMsg":           None,   # 'bea' for messages if execution begins, ends and aborts, you don't have to write all 3 letters
    "clusterName":          None,   # the name which will be shown by qstat, _ is not allowed on hpc2
    "clusterType":          0,      # 0 = inf - cluster with Torque-System | 1 = hpc2 with PBSPro
    "clusterWtime":         None,   # time after your program will be aborted, defaults: hpc2 - 48h | inf - 168h
    "coverageLevel":        1,      # height at which 2d coverage calculation will be performed
    "coverageMaxLevel":     1,      # 3d calculation will be performed between coverageLevel and coverageMaxLevel
    "deadDistance":         0.5,    # minimal distance between events
    "debugLevel":           2,      # 1: just config and outputfile
                                    # 2: +files for 2D-Viewer
                                    # 3: +files for 3D-Viewer
                                    # 4: complete tmp-folder
                                    # 5: +debug-messages
    "debugRays":            False,  # set True to draw rays in 3d-Viewer
    "diffractionThreshold": 0.125*7,  #influence range of edges
    "groundHeight":         0,      # used for osm maps, sets height of ground
    "interference":         False,  # enable/disable multi-path effects
    "mapName":              None,   # don't edit this. It will be set from script
    "maxIterations":        50,     # force stop when a ray is reflected very often
    "name":                 "auto", # sets name of outputfile: <mapname>_name. Set value to auto if u just want a timestamp (%Y%m%d-%H%M%S) after mapname
    "maxRange":             0,      # don't calculate signal strength if distance between receiver and transmitter is to far, will speed up calculation for larger maps
    "numberWorkers":        4,      # number of workers, only coverage maps are calculated in parallel, should be the number of cpu-cores
    "port":                 None,   # not used, default port is 4242, you can change it in src/util/networking.py
    "ppServers":            (),     # specify tuple of ppServers for cluster computing (doesn't work, although it should -> incompatible versions? network configuration? problem finding raylauncher? unfortunately no useful error message)
                                    # use param calculationServers if you want parallel caluclation (replaces ppServers with a self-built solution),
    "preprop" :             True,   # set this to false if you already done the preparation for a map, make sure parameter 'name' is the same
    "rayNumber":            5000,   # number of rays launched at sources
    "receivers":            "auto", # set specific receiver here, if you want to calculate just some links [[0,0,1],[1,1,1],...], 'auto' for full coverage or 'street' for street coverage
    "receiverType":         0,      # default value 0, set by script, dont change!
    "receiveThreshold":     "full", # size of "antenna", set to full and it will be calculated by script to sqrt(3 * (ss ** 2)) / 2.
    "reflectionPart":       0.153,  # sets what part of the incoming energy is reflected
    "scatteringPart":       0.0181, # sets what part of the incoming energy is scattered
    "stepSize":             1,      # discretization of the coverage maps
    "terrainHeight":        2,      # resolution of terrain  #ray-caster
    "terrainLevel":         "auto", # make a flat terrain instead of analyzing building heights
    "terrainWidth":         2,      # resolution of terrain
    "timeout":              0,      # timeout in seconds of a single job: one job is one receiver <-> transmitter link,
    "transmitters":         [[0, 0, 1]],  # coverage maps will be calculated for each position, use 'area' or 'cubic' for full coverage or 'street' for street coverage
    "transmitterType":      0,      # default value 0, set by script, dont change!
    "transmitterHeight":    1,      # used if transmitter are placed along streets
    "wavelength":           3e8 / 2.4e9
}


def evaluateConfig(config):
    if not isinstance(config["borders"], list) or len(config["borders"]) not in [0,4]:
        raise TypeError ("Borders should be a list of 4 integers or empty")
    if not isinstance(config["buildingHeight"], int) or config["buildingHeight"] <= 0:
        raise TypeError ("BuildingHeight should be an integer and >= 0")
    if not isinstance(config["calculationServers"], tuple):
        raise TypeError ("CalculationServers should be a tuple")
    if config["center"] is not None and (not isinstance(config["center"], list) or len(config["center"]) is not 3):
        raise TypeError ("Center should be a list of 3 integers or None")
    if not isintorfloat(config["coverageLevel"]) or config["coverageLevel"] < 0:
        raise TypeError ("CoverageLevel should be a number (int or float) and >= 0")
    if not isintorfloat(config["coverageMaxLevel"]) or config["coverageLevel"] > config["coverageMaxLevel"]:
        raise TypeError ("CoverageMaxLevel should be a number (int or float) and >= coverageLevel")
    if not isintorfloat(config["deadDistance"]) or config["deadDistance"] < 0:
        raise TypeError ("DeadDistance should be a number (int or float) and >= 0")
    if not isinstance(config["debugLevel"], int) or config["debugLevel"] not in [LOG1, LOG2, LOG3, LOGFULL, DEV]:
        raise TypeError ("DebugLevel should be an integer between " + str(LOG1) + " and " + str(DEV))
    if not isinstance(config["debugRays"], bool):
        raise TypeError ("DebugRays should be True or False")
    if not isintorfloat(config["diffractionThreshold"]) or config["diffractionThreshold"] < 0:
        raise TypeError ("Diffractionthreshold should be a number (int or float) and >= 0")
    if not isinstance(config["groundHeight"], int) or config["groundHeight"] < 0:
        raise TypeError ("GroundHeight should be an integer and >= 0")
    if not isinstance(config["interference"], bool):
        raise TypeError ("Interference should be True or False")
    if not isinstance(config["maxIterations"], int) or config["maxIterations"] <= 0:
        raise TypeError ("MaxIterations should be an integer and > 0")
    if not isinstance(config["name"], str):
        raise TypeError ("Name should be a string")
    if not isinstance(config["maxRange"], int) or config["maxRange"] < 0:
        raise TypeError ("MaxRange should be an integer and >= 0")
    if not isinstance(config["numberWorkers"], int) or config["numberWorkers"] <= 0:
        raise TypeError ("NumberWorkers should be an integer and > 0")
    if not isinstance(config["ppServers"], tuple):
        raise TypeError ("Ppservers should be a tuple")
    if not isinstance(config["rayNumber"], int) or config["rayNumber"] <= 0:
        raise TypeError ("RayNumber should be an integer and > 0")
    if config["receivers"] not in ["auto","full","street"] and not isinstance(config["receivers"], list) and not os.path.isfile(config["receivers"]):
        raise TypeError ("Receivers should be either 'auto' or 'full' or 'street' or a list of lists")
    if isinstance(config["receivers"], list) and not isinstance(config["receivers"][0], list):
        raise TypeError ("Your receivers-list should have the following format: [[x,y,z]] or [[x0,y0,z0],...,[xn,yn,zn]]")
    if not isinstance(config["receiverType"], int):
        raise TypeError ("ReceiverType should be an integer. DO NOT change this value manually!")
    if not config["receiveThreshold"] == "full" and not isinstance(config["receiveThreshold"],(int, float, str)) or config["receiveThreshold"] <= 0:
        raise TypeError ("ReceiveThreshold should be a number (int or float) and > 0 or 'full'")
    if not isintorfloat(config["reflectionPart"]) or config["reflectionPart"] < 0:
        raise TypeError ("ReflectionPart should be a number (int or float) and >= 0")
    if not isintorfloat(config["scatteringPart"]) or config["scatteringPart"] < 0:
        raise TypeError ("ScatteringPart should be a number (int or float) and >= 0")
    if not isintorfloat(config["stepSize"]) or config["stepSize"] <= 0:
        raise TypeError ("StepSize should be a number (int or float) and > 0")
    if not isinstance(config["terrainHeight"], int) or config["terrainHeight"] < 0:
        raise TypeError ("TerrainHeight should be an integer and >= 0")
    if config["terrainLevel"] is not "auto" and not isintorfloat(config["terrainLevel"]):
        raise TypeError ("TerrainLevel should be 'auto' or a number (int or float)")
    if not isinstance(config["terrainWidth"], int) or config["terrainWidth"] < 0:
        raise TypeError ("TerrainWidth should be an integer and >= 0")
    if not isinstance(config["timeout"], int) or config["timeout"] < 0:
        raise TypeError ("Timeout should be an integer and >= 0")
    if config["transmitters"] not in ["area","cubic","street"] and not isinstance(config["transmitters"], list) and not os.path.isfile(config["transmitters"]):
        raise TypeError ("Transmitters should be either 'area' or 'cubic' or 'street' or a list of lists")
    if isinstance(config["transmitters"], list) and not isinstance(config["transmitters"][0], list):
        raise TypeError ("Your transmitters-list should have the following format: [[x,y,z]] or [[x0,y0,z0],...,[xn,yn,zn]]")
    if not isinstance(config["transmitterType"], int):
        raise TypeError ("TransmitterType should be an integer. DO NOT change this value manually!")
    if not isintorfloat(config["wavelength"]) or config["wavelength"] <= 0:
        raise TypeError ("Wavelength should be a number (int or float) and > 0")



def isintorfloat(param):
    return isinstance(param, int) or isinstance(param, float)
