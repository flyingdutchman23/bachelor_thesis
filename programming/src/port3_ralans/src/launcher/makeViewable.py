
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
import pickle
import marshal
import sys


def makeViewable(textfile, binfile):
    ACTIVE = 0
    ABORTED = 1
    SUCCEEDED = 2
    MAYBE_RECEIVED = 4
    RECEIVED = 5
    with open(textfile) as f:
        vertices = []
        for l in f:
            inarr = np.genfromtxt(StringIO(l), delimiter=" ")
            origin = inarr[0:3]
            direction = inarr[3:6]
            energy = inarr[6]
            status = inarr[7]
            dest = origin + direction
            color = [1, 0, 0]
            if status == ABORTED:
                color = [1, 1, 0]
            if status == SUCCEEDED:
                color = [0, 1, 0]
            if status == MAYBE_RECEIVED:
                color = [0, 1, 1]
            if status == RECEIVED:
                color = [0, 0, 1]
            vertices.append(origin[0])
            vertices.append(origin[1])
            vertices.append(origin[2])
            vertices.extend(color)
            vertices.append(dest[0])
            vertices.append(dest[1])
            vertices.append(dest[2])
            vertices.extend(color)

    vertices = (np.array(vertices)).tolist()
    with open(binfile, 'wb') as output:
        marshal.dump(vertices, output)


if __name__ == "__main__":
    textfile = sys.argv[1]
    binfile = sys.argv[2]
    makeViewable(textfile, binfile)
