
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
from io import StringIO

import src.globals as gl

def removeOffset(buildings, outfilename, center=None):
    return removeOffsetWithStreets(buildings, None, outfilename, None, center)

def removeOffsetWithStreets(buildings, streets, buildingsOut, streetsOut, center=None):
    gl.logger.debug("parsing...")

    if center is None:

        acc = getPolys(buildings, None)
        #print len(acc)

        if acc is None:
            center = [0, 0, 0]
        else:
            center = np.mean(acc, axis=0)


    gl.logger.debug("...got center...")
    gl.logger.info("Center: " + str(center))


    i = saveWoOffset(buildings, buildingsOut, center)
    if streets:
        i += saveWoOffset(streets, streetsOut, center)

    gl.logger.debug(str(i) + " polygons")


def saveWoOffset(fi, fo, center):
    i = 0
    with open(fi) as fi:
        with open(fo, 'w') as fo:
            for l in fi:
                inarr = np.genfromtxt(StringIO(l), delimiter=" ")

                #remove offset to avoid floating precision problems
                inarr = [inarr - np.tile(center, len(inarr) / 3)]

                np.savetxt(fo, inarr)
                i += 1
    return i


def getPolys(fi, list):
    with open(fi) as fb:
        for l in fb:
            inarr = np.genfromtxt(StringIO(l), delimiter=" ")
            if list is None:
                list = [inarr[0:3]]
            else:
                list = np.append(list, [inarr[0:3]], axis=0)
    return list
