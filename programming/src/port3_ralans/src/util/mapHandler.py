
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

dolog = True


class MapHandler:
    def __init__(self, filename):
        self.grids = []
        res = []
        xl = None
        yl = None
        with open(filename) as f:
            for i, l in enumerate(f):
                inarr = np.genfromtxt(StringIO(l), delimiter=" ")
                if i == 0:
                    self.borders = inarr
                else:
                    if len(inarr) < 4:
                        if i > 1:
                            self.grids.append(res)
                            res = []
                            if yl == None:
                                yl = len(res)
                            else:
                                if yl != len(res) and dolog:
                                    print("yl not equal in line %d : %d %d" % (i, yl, len(res)))

                    else:
                        res.append(np.array(inarr))
                        if xl == None:
                            xl = len(inarr)
                        else:
                            if xl != len(inarr) and dolog:
                                print("xl not equal in line %d : %d %d" % (i, xl, len(inarr)))
                                # don't forget the last one:
        self.grids.append(res)
        res = []
        if yl == None:
            yl = len(res)

        self.xlen = len(self.grids[0])
        self.ylen = len(self.grids[0][0])
        if len(self.grids) != self.xlen * self.ylen and dolog:
            print("receiver grid size doesn't match transmitter grid size %d %d %d" % (
            self.xlen, self.ylen, len(self.grids)))
            print("grid", self.grids)

    def getLink(self, transmitter, receiver):
        txi = int((transmitter[0] - self.borders[0]) / self.borders[2])
        tyi = int((transmitter[1] - self.borders[1]) / self.borders[3])
        rxi = int((receiver[0] - self.borders[0]) / self.borders[2])
        ryi = int((receiver[1] - self.borders[1]) / self.borders[3])
        value = -3000.0
        try:
            value = self.grids[tyi * self.xlen + txi][ryi][rxi]
        except:
            if dolog:
                print("unable to pick :")
                print(txi, tyi, rxi, ryi, self.xlen, self.ylen)
        return value