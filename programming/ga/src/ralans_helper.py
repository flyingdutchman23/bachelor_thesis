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
import numpy as np
import io
import sys
import zipfile
from constants import AREA, CUBIC, POINT, LIST, XAXIS, YAXIS, ZAXIS
from my_util import frange

# the name of the result file in RaLaNS
RESULTFILENAME = 'result.txt'
# the name of the config file in RaLaNS
CONFIGFILENAME = 'config.cfg'
# the directory for the polygons
POLYGONSDIR = 'polygons/'
# the filename for the buildings
BUILDINGSFILENAME = 'buildings.txt'
# the path to the buildings file
BUILDINGSPATH = POLYGONSDIR + BUILDINGSFILENAME

def parseConfigFile(filename, isZip=True):
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

def getFiles(zipf):

    zf = zipfile.ZipFile(zipf, 'r')

    resfile = zf.open(RESULTFILENAME)
    configfile = zf.open(CONFIGFILENAME)

    bdfile = None
    try:
        bdfile = zf.open(BUILDINGSPATH)
    except:
        print("No polygon file found! Will not draw buildings on the map.")

    zf.close()

    return resfile, configfile, bdfile

def getTransmitters(filename, isZip=False):
    """
    if type(filename) is zipfile.ZipExtFile:
        f = filename
    else:
        f = open(filename)
    """
    if isZip:
        f = filename
    else:
        f = open(filename)

    input = f.read().split('\n')

    f.close()

    # remove lastline
    input = input[0:-1]

    # First line contains transmitter metainformation
    headtr = np.genfromtxt(io.StringIO(input[0]))

    transmitters = parseTransmitterHeader(headtr)

    return transmitters


def get_nextid_by_pos(reqpos, positions, max_dist=float('inf')):

    trid = None
    min_dist = float('inf')

    for i, pos in enumerate(positions):
        dist = np.linalg.norm(np.subtract(reqpos,pos))
        if dist < min_dist and dist <= max_dist:
            trid = i
            min_dist = dist

    if trid == None:
        print("Transmitter not found")

    return trid

def conv_byte_to_str(line):
    """converts a readed line of bytes into a line, which is a string. if the line is
    already a string it just returns the string.

    :line: the line, which should be either a string or a line of bytes
    :returns: the line decoded as a string

    """
    if isinstance(line,bytes):
        line = line.decode('utf8')
    return line

def parseHead(head, type):
    stp = [0, 0, 1]
    leng = [0, 0, 1]
    height = [0, 0]
    borders = [0, 0, 0, 0]

    if type == AREA:
        height[0] = height[1] = head[5]
        stp[0] = head[6]
        stp[1] = head[7]
        borders = head[1:5]
        leng[0] = int((borders[2] - borders[0]) / stp[0]) + 1
        leng[1] = int((borders[3] - borders[1]) / stp[1]) + 1

    elif type == CUBIC:
        stp = head[7:]
        borders[:2] = head[1:3]
        borders[2:] = head[4:6]
        height[0] = head[3]
        height[1] = head[6]
        leng[0] = int((borders[2] - borders[0]) / stp[0]) + 1
        leng[1] = int((borders[3] - borders[1]) / stp[1]) + 1
        leng[2] = int((height[1] - height[0]) / stp[2]) + 1

    elif type == LIST:
        leng = head[1]
        stp = head[2:]
    else:
        sys.exit('no correct result file from RaLaNS!')


    return borders, stp, height, leng

def parseBorders(input):
    print('input: ', input)
    input = conv_byte_to_str(input)
    return np.loadtxt(io.StringIO(input.strip()), delimiter=" ").tolist()

def parseTransmitterHeader(head):
    # print("header: ",head)
    transmitters = []
    transmitterType = int(head[0])

    if transmitterType == POINT:
        sys.exit('POINT is not supported!!!')

    elif transmitterType == LIST:

        headtr = head[2:]
        while len(headtr) > 0:
            transmitter = [headtr[XAXIS], headtr[YAXIS], headtr[ZAXIS]]
            headtr = headtr[3:]
            transmitters.append(transmitter)

    # not very fast, but functional
    elif transmitterType == AREA:
        borders, stp, height, _ = parseHead(head, transmitterType)
        for y in frange(borders[1], borders[3], stp[1]):
            for x in frange(borders[0], borders[2], stp[0]):
                transmitters.append([x, y, height[0]])

    elif transmitterType == CUBIC:
        borders, stp, height, _ = parseHead(head, transmitterType)
        for z in frange(height[0], height[1], stp[2]):
            for y in frange(borders[1], borders[3], stp[1]):
                for x in frange(borders[0], borders[2], stp[0]):
                    transmitters.append([x, y, z])

    return transmitters
