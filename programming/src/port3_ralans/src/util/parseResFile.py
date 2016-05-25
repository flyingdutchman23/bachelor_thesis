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
from . import zipfile_

from ..util.functions import frange

POINT = 0
LINE = 1
AREA = 2
CUBIC = 3
LIST = 4

DEBUG = 0


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


def getTransmitterID(reqTr, transmitters, stepsize=1, list=True):
    print("Stepsize =", stepsize)
    trid = -1
    i = 0
    for tr in transmitters:
        tr = np.array(tr)
        if reqTr is None or np.linalg.norm(reqTr - tr) < stepsize / 2.:
            if DEBUG and reqTr is not None:
                print("found")
            trid = i
            break
        i += 1

    if trid == -1:
        print("Transmitter not found")
        trid = 0

    if list:
        for i, t in enumerate(transmitters):
            print(i, t)
    return trid


"""
# Read in the file once and build a list of line offsets
line_offset = []
offset = 0
for line in file:
    line_offset.append(offset)
    offset += len(line)
file.seek(0)

# Now, to skip to line n (with the first line being line 0), just do
file.seek(line_offset[n])
"""

def conv_byte_to_str(line):
    """converts a readed line of bytes into a line, which is a string. if the line is
    already a string it just returns the string.

    :line: the line, which should be either a string or a line of bytes
    :returns: the line decoded as a string

    """
    if isinstance(line,bytes):
        line = line.decode('utf8')
    return line


def parseResFile(filename, requestedTransmitter, stepsize=1, requestedLayer=None, isZip=False):
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

    line = conv_byte_to_str(f.readline())
    print("type line: ", type(line))
    headtr = np.loadtxt(io.StringIO(line), delimiter=" ")
    # headtr = np.loadtxt(io.StringIO(testline), delimiter=" ")
    print("headtr: ", headtr)
    transmitters = parseTransmitterHeader(headtr)
    print("Transmitters available: ", len(transmitters))
    trid = getTransmitterID(requestedTransmitter, transmitters, stepsize)
    if DEBUG: print("Id of selected transmitter: ", trid)

    line = conv_byte_to_str(f.readline())
    headrec = np.loadtxt(io.StringIO(line), delimiter=" ")
    t = int(headrec[0])
    borders, stp, height, leng = parseHead(headrec, t)
    if DEBUG: print("bd, steps, height, len:", borders, stp, height, leng)

    if requestedLayer is not None:
        try:
            requestedLayer = int(requestedLayer)
            layer = leng[2]
            if layer < requestedLayer or requestedLayer == 0:
                print("This file has only ", layer, "layers. Using first one.")
                layer = 0
            else:
                layer = requestedLayer - 1  # we dont need the offset for the first layer
        except ValueError:
            layer = 0
            print("invalid layer")
    else:
        print("No layer given, using first one.", type(requestedLayer))
        layer = 0
    print("Displaying transmitter:", transmitters[trid])
    print("Displaying layer:", layer + 1)

    res = []

    if t in [CUBIC, AREA]:
        sy = leng[1]
        layers = leng[2]

        start = sy * layers * trid
        off = layer * sy

        if DEBUG: print(sy, layer, trid, start, off)
        if DEBUG: print(start + off, start + off + sy)
        for i, l in enumerate(f):
            if i < start + off:
                continue
            elif start + off <= i < start + off + sy:
                if len(l.strip()) > 0:
                    l = conv_byte_to_str(l)
                    res.append(np.loadtxt(io.StringIO(l), delimiter=" ").tolist())
            else:
                break

    if t in [LINE, LIST]:
        borders_ = parseBorders(f.readline())
        if t == LIST:
            borders = borders_
        print("line,", borders)
        for i, l in enumerate(f):
            if i < trid:
                continue
            elif i == trid:
                if len(l.strip()) > 0:
                    l = conv_byte_to_str(l)
                    res.append(np.loadtxt(io.StringIO(l), delimiter=" ").tolist())
            else:
                break

    f.close()

    # res = parseArea(input)
    if DEBUG: print("Längen:", len(res), len(res[0]))
    # print res


    for y in range(0, len(res)):
        for x in range(0, len(res[y])):
            if res[y][x] < -1000:
                res[y][x] = np.inf

    return np.array(res), borders, transmitters[trid], stp


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

    if type == CUBIC:
        stp = head[7:]
        borders[:2] = head[1:3]
        borders[2:] = head[4:6]
        height[0] = head[3]
        height[1] = head[6]
        leng[0] = int((borders[2] - borders[0]) / stp[0]) + 1
        leng[1] = int((borders[3] - borders[1]) / stp[1]) + 1
        leng[2] = int((height[1] - height[0]) / stp[2]) + 1

    if type == POINT:
        borders[:2] = head[1:3]
        height[0] = head[3]

    if type == LINE:
        borders[:2] = head[1:3]
        borders[2:] = head[4:6]
        height[0] = head[3]
        height[1] = head[6]
        stp[2] = head[7]

    if type == LIST:
        leng = head[1]
        stp = head[2:]

    return borders, stp, height, leng


def parseTransmitterHeader(head):
    print("header: ",head)
    transmitters = []
    transmitterType = int(head[0])

    if transmitterType == POINT:
        transmitters.append([head[1], head[2], head[3]])

    elif transmitterType == LIST:

        headtr = head[2:]
        while True:
            # print len(headtr)
            if len(headtr) == 0:
                break
            # print len(headtr)
            transmitter = [headtr[0], headtr[1], headtr[2]]
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


def parseBorders(input):
    return np.genfromtxt(io.StringIO(input.strip()), delimiter=" ").tolist()
