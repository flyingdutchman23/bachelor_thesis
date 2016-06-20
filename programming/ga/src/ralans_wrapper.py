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

import config

from port3_ralans.viewer2d import getFiles

DEBUG = 0

# stores the arrays for the signals, will be a 2d arrays of the form:
# signals[transmitterid][receiverid]
signals = None

def init():
    """initializes the RaLaNS module. Loads the data from the result file into a 2d
    signals array for better use later.

    """
    print('FILENAME: ', config.FILENAME)
    print('LENG: ', config.LENG)
    print('COVERAGE_LEVEL: ', config.COVERAGE_LEVEL)
    resfile, _, _ = getFiles(config.FILENAME)
    read_resultfile(resfile, True)
    resfile.close()

def read_resultfile(filename, isZip=True):
    """ reads the result file and stores all the signals into a 2d signals array,
    which is then accesible via another function. 

    :filename: the file, can be an already opened zip file, or just the filename. e.g. as
    a string. If it is a zip file, it has to be specified with the other argument isZip.

    :isZip: should be true, if the given file is an opened zip. Should be false, if it is
    just a represenation of the filepath, so that the function will open it.

    """
    if isZip:
        f = filename
    else:
        f = open(filename)

    print('1st line: ', f.readline())
    print('2nd line: ', f.readline())
    print('size YAXIS * ZAXIS: ', config.LENG[config.YAXIS] * config.LENG[config.ZAXIS])
    print('config.IND_LEN: ', config.IND_LEN)
    print('config.LENG: ', config.LENG)

    # assert config.PLACEMENT_TYPE in [config.CUBIC, config.AREA], \
            # "Only AREA and CUBIC for testing!"

    # init the big signals arrays with NaN values to see mistakes quicker
    # this array just allows files, which have the same transmitters as receivers
    global signals
    signals = np.NAN * np.empty((config.IND_LEN, config.IND_LEN))


    if config.PLACEMENT_TYPE in [config.CUBIC, config.AREA, config.LIST]:

        if config.PLACEMENT_TYPE == config.LIST:
            borders = parseBorders(f.readline())
            print("border in result: ", borders)
            assert len(borders) == 4
            config.BORDERS = borders

        trid = 0
        cur_trans_signals = []
        receiver_count = 0
        for line_index, line in enumerate(f):

            # to check that all transmitter ids are smaller than the total number of
            # transmitters
            assert trid < config.IND_LEN, \
                    "There are more transmitters in the file than apparently specified"

            line = conv_byte_to_str(line)
            new_signals = np.loadtxt(io.StringIO(line), delimiter=" ").tolist()
            assert len(new_signals) == config.LENG[config.XAXIS]
            cur_trans_signals.extend(new_signals)
            receiver_count += 1


            """
            yLen * zLen stands for the number of receivers each tranmitters has, so if that case 
            happens all receiver signals for that tranmitter are already in the numbers vector so 
            then all that signals will be added to the signals vector and the process goes again 
            until the lineCounter has has the value of yLen * zLen, so that all signals are read 
            for that tranmitter               
            """
            if receiver_count == config.LENG[config.YAXIS] * config.LENG[config.ZAXIS]:
                print('len signals 1 trans: ', len(signals[trid]))
                print('len cur trans signals: ', len(cur_trans_signals))
                assert len(signals[trid]) == len(cur_trans_signals)
                signals[trid][:] = cur_trans_signals 
                cur_trans_signals = []
                receiver_count = 0
                trid += 1

        check = np.array([signal == np.NAN for signal in signals])
        assert not check.any(), \
            "Some field in the signals array was not filled"
    else:
        sys.exit('The type has to be CUBIC, AREA or LIST!')

    f.close()

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

def get_signal(trid, recid):
    """returns the signal value for the connection from the given transmitter to the given
    receiver

    :trid: the id of the transmitter
    :recid: the id of the receiver
    :returns: the signal strength

    """
    return signals[trid][recid]

def packet_received_by_id(trid, recid):
    """calculates whether or not there is a connection from the transmitter given by its
    id to the receiver given by its id. Returns the result as a boolean. The THRESHOLD
    argument is important for this, because this function compares the result with that
    value to decide whether there is a connection or not.

    :trid: the id of the transmitter
    :recid: the id of the receiver
    :returns: True, if there is a connection.
              False, if there is no connection.

    """
    return get_signal(trid, recid) > config.THRESHOLD

def packet_received_by_positions(transmitter, receiver):
    """TODO: Docstring for packet_received.

    :transmitter: TODO
    :receiver: TODO
    :returns: TODO

    """
    trid = getTransmitterID(transmitter, config.POSITIONS, config.STEPSIZE, True)
    recid = getTransmitterID(receiver, config.POSITIONS, config.STEPSIZE, True)
    return packet_received_with_id(trid, recid)

def getTransmitterID(reqTr, transmitters, stepsize=1, toList=True):
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

    if toList:
        for i, t in enumerate(transmitters):
            print(i, t)

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

    if type == config.AREA:
        height[0] = height[1] = head[5]
        stp[0] = head[6]
        stp[1] = head[7]
        borders = head[1:5]
        leng[0] = int((borders[2] - borders[0]) / stp[0]) + 1
        leng[1] = int((borders[3] - borders[1]) / stp[1]) + 1

    elif type == config.CUBIC:
        stp = head[7:]
        borders[:2] = head[1:3]
        borders[2:] = head[4:6]
        height[0] = head[3]
        height[1] = head[6]
        leng[0] = int((borders[2] - borders[0]) / stp[0]) + 1
        leng[1] = int((borders[3] - borders[1]) / stp[1]) + 1
        leng[2] = int((height[1] - height[0]) / stp[2]) + 1

    elif type == config.LIST:
        leng = head[1]
        stp = head[2:]
    else:
        sys.exit('no correct result file from RaLaNS!')


    return borders, stp, height, leng


def parseBorders(input):
    print('input: ', input)
    input = conv_byte_to_str(input)
    return np.loadtxt(io.StringIO(input.strip()), delimiter=" ").tolist()
