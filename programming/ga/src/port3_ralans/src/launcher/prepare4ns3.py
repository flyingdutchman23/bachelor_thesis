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
import marshal
import sys
import io


from src.launcher import wrapLauncher as wl



def prepare4ns3(coveragefolder, outfilename, borders, config):


    transmitters = config["transmitters"]

    with open(outfilename, "wb") as outfile:
        #write Heads
        headt = createTransmitterMeta(config)
        headr = wl.createTypeString(config) + "\n"
        outfile.write(str(headt))
        outfile.write(str(headr))
        if config["receiverType"] in [1,4]:
            borders = str(borders[0]) + ' ' + str(borders[1]) + ' ' + str(borders[2]) + ' ' + str(borders[3]) + '\n'
            outfile.write(borders)

        for transmitter in transmitters:
            x,y,z = transmitter
            #print transmitter, x, y, z
            string = "[{0:g}, {1:g}, {2:g}].txt".format(x,y,z)
            filename = coveragefolder + string
            #print filename
            with open(filename, 'r') as file:
                for l in file.readlines():
                #readlines() is faster, but stores the whole file into ram
                #for l in file:
                    if len(l.strip()) > 0:
                        row = np.genfromtxt(io.StringIO(l), delimiter=" ").tolist()
                        row = np.array(row).flatten()
                        row += (row == 0) * sys.float_info.min
                        row = 10.0 * np.log10(row)
                        np.savetxt(outfile, [row])
            if config["debugLevel"] == 5: print("Prepared result of transmitter:", transmitter)


def createTransmitterMeta(config):

    type = config["transmitterType"]
    transmitters = config["transmitters"]

    out = str(type)
    minx = config["borders"][0]
    maxx = config["borders"][2]
    miny = config["borders"][1]
    maxy = config["borders"][3]
    step = config["stepSize"]
    minz = config["coverageLevel"]
    maxz = config["coverageMaxLevel"]
    sx = sy = sz = step

    if type == 0:
        out += " " + str(transmitters[0][0]) + " " + str(transmitters[0][1]) + " " + str(transmitters[0][2])
    if type == 2:
        out += " " + str(minx) + " " + str(miny) + " " + str(maxx) + " " + str(maxy) + " " + str(minz) + " " + str(sx) + " " + str(sy)
    if type == 3:
        out += " " + str(minx) + " " + str(miny) + " " + str(minz) + " " + str(maxx) + " " + str(maxy) + " " + str(maxz) + " " + str(sx) + " " + str(sy) + " " + str(sz)
    if type == 1:
        # UGLY HACK, interpret line as list
        out = str(4)
        type = 4
        """
        line = config["transmitters"][0]
        start, end, step = line
        out += " " + str(start[0]) + " " + str(start[1]) + " " + str(start[2]) + " " + str(end[0]) + " " + str(end[1]) + " " + str(end[2]) + " " + str(step)
        """
    if type == 4:
        out += " " + str(len(transmitters))
        for transmitter in transmitters:
            out += " " + str(transmitter[0]) + " " + str(transmitter[1]) + " " + str(transmitter[2])


    out += "\n"
    return out



if __name__ == "__main__":
    coveragefolder = "coverage/"
    filename = 'coverage4ns3.txt'
    borders = [-50, -30, 50, 30]
    config = {"stepSize": 2}

    prepare4ns3(coveragefolder, filename, borders, config)


