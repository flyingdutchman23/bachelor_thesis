# -*- coding: utf-8 -*-
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

import sys
import collections
import numpy as np
from io import StringIO

from ..config import *
from ..globals import copy

#backport of zipfile for python versions between 2.7.0 to 2.7.9
#backport not working for version 2.6
if sys.version_info[0] == 2 and sys.version_info[1] == 7 and sys.version_info[2] < 9:
    from src.util import zipfile_ as zipfile
else:
    import zipfile

def saveConfigFile(config, filename, configfolder=fConfigfiles):
    """ Stores dictionary config as file
        Keys are sorted in alphabetical order
    :param config: Dictionary with config parameters
    :param filename: Filename
    """

    #OrderedDict introduced in 2.7, only used for better readability
    try:
        od = collections.OrderedDict(sorted(config.items()))
    except AttributeError:
        od = config

    with open(configfolder+filename, "w") as f:
        for k, v in list(od.items()):
            if isinstance(v, str):
                f.write(k + " = '" + str(v) + "'\n")
            else:
                f.write(k + " = " + str(v) + "\n")

def parseConfigFile(filename, isZip=False):
    """
    Parses a configfile as dictionary
    :param filename: Filename
    :param configfolder: Folder, which contains the configfile
    :return: Dictionary containing all key-values pares of the file
    """
    config = {}

    if isZip:
        f = filename
    else:
        f = open(filename)

    for line in f:
        # print(line)
        line = line.decode('utf8')
        s = line.split("#")[0].split(" = ")
        if len(s) > 1:
            try:
                config[s[0].strip()] = eval(s[1])
            except:
                config[s[0].strip()] = s[1].strip()

    f.close()

    return config


def parseTransmitterFile(filename):
    """
    Parses a file with transmitter or receiver positions
    :param filename: Filename, with folders
    :return: List of positions
    """
    transmitter = []
    with open(filename) as f:
        for line in f:
            t = line.split(" ")
            for tr in t:
                try:
                    transmitter.append(eval(tr))
                except:
                    pass
    return transmitter


def saveTransmitterFile(transmitter, filename):
    """
    Saves a list of positions as file
    :param transmitter: List of positions
    :param filename: Full filename with folders
    """
    f = open(filename, "w")

    i = 0
    for t in transmitter:
        f.write(str(t) + " ")
        i += 1
        if i%6 == 0:
            f.write("\n")

    f.close()


def parsePositionsFile(filename):
    """
    Parses a input file with positions
    :param filename: Full filename with folder
    :return:
        type: 1 or 4,
        positions: A list with positions
    """
    validTypes = [1,4]

    f = open(filename)
    file = f.read().split("\n")
    type = int(file[0][0])

    if type not in validTypes:
        print("Invalid type for positions. Line - 1 | List - 4 \n Exiting...")
        sys.exit()

    positions = []
    if type == 4:
        for line in file[1:]:
            t = line.split("#")[0].split(" ")
            for tr in t:
                try:
                    positions.append(eval(tr))
                except:
                    pass

    if type == 1:
        for line in file[1:]:
            t = line.split("#")[0].split(" ")
            try:
                l = (eval(t[0]), eval(t[1]), float(t[2]))
                positions.append(l)
            except:
                pass

    f.close()
    return type, positions


def savePositions4Launcher(points, filename):
    """
    Saves positions in a way the
    :param points:
    :param filename:
    :return:
    """
    f = open(filename, "w")

    for t in points:
        if isinstance(t, tuple):
            start, end, step = t
            for v in start, end:
                for p in v:
                    f.write(str(p) + " ")
            f.write(str(step) + " ")
        else:
            for p in t:
                f.write(str(p) + " ")
        f.write("\n")

    f.close()

def line2List(lines):
    positions = []

    if isinstance(lines, tuple):
        lines = [lines]

    for l in lines:

        (start, end, step) = l
        vec = np.array(end) - np.array(start)
        leng = np.linalg.norm(vec)
        vec = vec/leng
        vec *= step
        current = np.array(start)

        while np.linalg.norm(np.array(current) - np.array(start)) <= leng:
            positions.append(current.tolist())
            current = np.array(current) + np.array(vec)

    return positions

def mergeDict(dictFrom, dictTo):
    for k, v in list(dictFrom.items()):
        if k not in list(dictTo.keys()):
            dictTo[k] = v
    return dictTo

def calculatePositionFromStreet(file, step, height = 1):
    print("Calculate positions on streets.")
    positions = []
    with open(file) as sf:
        for l in sf:
            coord = np.genfromtxt(StringIO(l), delimiter=" ")
            for i in range(0, (len(coord) -1)/3, 1):
                start = np.array((coord[i*3],coord[i*3+1], height))
                end = np.array((coord[i*3+3], coord[i*3+4], height))
                vec = np.array(end) - np.array(start)
                leng = np.linalg.norm(vec)
                vec = vec/leng*step
                cur = start

                while np.linalg.norm(np.array(cur) - np.array(start)) <= leng:
                    positions.append(cur.tolist())
                    cur = np.array(cur) + np.array(vec)
    print("Calculated", len(positions), "positions.")
    return positions


def createIdentifier(cfg):
    try:
        return cfg["mapName"] + '_' + cfg["name"]
    except KeyError:
        return None


def saveAsZip(identifier, workfolder, dlvl = 2, rays = False):

    zipfname = fOutputfiles + identifier + '.zip'

    zipf = zipfile.ZipFile(zipfname, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)

    if dlvl >= 1:
        zipf.write(fOutputfiles + identifier + '.txt', 'result.txt')
        zipf.write(fConfigfiles + identifier + '.cfg', 'config.cfg')
        rec = workfolder + identifier + "_receiver.rec"
        tr = fConfigfiles + identifier + "_transmitter.tr"
        if os.path.isfile(rec):
            zipf.write(rec, 'receivers.rec')
        if os.path.isfile(tr):
            zipf.write(tr, 'transmitters.tr')
    if dlvl >= 3:
        zipf.write(fViewerConfig + identifier + '.vcfg', 'config.vcfg')

    if dlvl < 4:
        for file in [logEdge, logLauncher, logScript]:
            zipf.write(workfolder+fLogs+file, fLogs+file)

        if dlvl >= 2:
            zipf.write(workfolder + fPolygons + fileBuildings, fPolygons + fileBuildings)

        if dlvl >= 3:
            zipf.write(workfolder + fPolygons + binBuildings, fPolygons + binBuildings)
            zipf.write(workfolder + fPolygons + binTerrain, fPolygons + binTerrain)
            zipf.write(workfolder + fEdges + binBuildings, fEdges + binBuildings)
            zipf.write(workfolder + fEdges + binTerrain, fEdges + binTerrain)
            if rays:
                for root, _, files in os.walk(workfolder + fRays):
                    for file in (file for file in files if file.split('.')[-1] == 'bin'):
                        zipf.write(os.path.join(root, file), fRays + file)


    else:
        for root, dirs, files in os.walk(workfolder):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.join(root.split('/')[-1], file))

    zipf.close()



def saveViewerConfig(identifier, config):
    with open(fViewerConfig + identifier + '.vcfg', 'w') as f:

        folder = identifier + '/'
        f.write(fPolygons + binBuildings + '\t(0.8,0.8,0.8,0.1)\t0\tGL_TRIANGLES\n')
        f.write(fPolygons + binTerrain + '\t(0.0,0.4,0.1)\t0\tGL_TRIANGLES\n')
        f.write(fEdges + binBuildings + '\t(1.0,1.0,1.0)\t0\tGL_LINES\n')
        #f.write(fTmp + folder + fEdges + binTerrain'\t(1.0,1.0,1.0)\t0\tGL_LINES\n')
        if config["debugRays"] is True:
            for transmitter in config["transmitters"]:
                x,y,z = transmitter
                transmitter = "[{0:g}, {1:g}, {2:g}]".format(x,y,z)
                f.write(fRays + str(transmitter) + '.bin\t(1.0,0.0,0.0)\t1\tGL_LINES\n')


def saveInConfigfolder(file, identifier, fconfig = fConfigfiles):
    filename = file.split("/")[-1]
    filetype = filename.split(".")[-1]
    filename = "receiver." if filetype == "rec" else "transmitter."
    copy(file, fconfig + identifier + "_" + filename + filetype)

def frange(x, y, jump):
    while x <= y:
        yield x
        x += jump
