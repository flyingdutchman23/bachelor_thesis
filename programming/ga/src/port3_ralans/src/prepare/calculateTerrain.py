
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

sys.path.append("./")
import src.globals as gl

mapwidth = 100
mapheight = 100

SIGMA = 1e-10


def pushTriangle(a, b, c, arr):
    """
    Add vertices and normals of a triangle described by a,b,c to arr.
    """
    # print a,b,c
    normal = np.cross(a - b, c - b)
    #no triangles without area:
    if np.abs(np.dot(normal, normal)) > SIGMA:
        normal /= np.linalg.norm(normal)
        #print normal
        arr.extend(a)
        arr.extend(normal)
        arr.extend(b)
        arr.extend(normal)
        arr.extend(c)
        arr.extend(normal)
    return arr


def calculateGML(filename, outfilename, config):
    mapwidth = config["terrainWidth"]
    mapheight = config["terrainHeight"]
    with open(filename) as f:
        vertices = []
        acc = None
        for l in f:
            inarr = np.genfromtxt(StringIO(l), delimiter=" ")
            for vec in np.split(inarr, len(inarr) / 3):
                if acc is None:
                    acc = [vec]
                else:
                    acc = np.append(acc, [vec], axis=0)

    if acc is None and "borders" in list(config.keys()):
        minx = config["borders"][0]
        miny = config["borders"][1]
        maxx = config["borders"][2]
        maxy = config["borders"][3]
        minz = config["coverageLevel"]
        maxz = config["coverageMaxLevel"]
    else:
        minx = np.amin(acc, axis=0)[0]
        miny = np.amin(acc, axis=0)[1]
        minz = np.amin(acc, axis=0)[2]
        maxx = np.amax(acc, axis=0)[0]
        maxy = np.amax(acc, axis=0)[1]
        maxz = np.amin(acc, axis=0)[2]
    gl.logger.debug( str(minx) + " " + str(miny) + " " + str(maxx) + " " + str(maxy) )
    gl.logger.info( "Terrainsize: " + str((maxx - minx)*(maxy - miny)))
    meanheight = maxz / 2 + minz / 2
    heightmap = np.zeros((mapwidth, mapheight))
    dx = (maxx - minx) / (mapwidth - 1)
    dy = (maxy - miny) / (mapheight - 1)

    # normalizer=	np.tile([1.0/(maxx-minx),1.0/(maxy-miny),1.0/(maxz-minz)],(len(acc),1)) #normed distances

    for xi in range(0, mapwidth):
        for yi in range(0, mapheight):
            point = [minx + dx * xi, miny + dy * yi, minz]
            if config["terrainLevel"] == "auto":
                diffs = (np.tile(point, (len(acc), 1)) - acc)  #* normalizer
                diffssq = diffs * diffs

                distssq = np.sum(diffssq, axis=1)
                arg = np.argmin(distssq)
                heightmap[xi, yi] = acc[arg, 2]
            else:
                heightmap[xi, yi] = float(config["terrainLevel"])
    gl.logger.debug( "\n" + str(heightmap) )

    #vertices = []
    res = []
    for xi in range(0, mapwidth - 1):
        for yi in range(0, mapheight - 1):
            ul = np.array([minx + dx * xi, miny + dy * yi, heightmap[xi, yi]])  #-center
            ur = np.array([minx + dx * xi, miny + dy * (yi + 1), heightmap[xi, yi + 1]])  #-center
            ll = np.array([minx + dx * (xi + 1), miny + dy * yi, heightmap[xi + 1, yi]])  #-center
            lr = np.array([minx + dx * (xi + 1), miny + dy * (yi + 1), heightmap[xi + 1, yi + 1]])  #-center
            #first triangle:
            #vertices = pushTriangle(ur, ul, ll, vertices)
            #vertices = pushTriangle(ll, lr, ur, vertices)
            line = []
            line.extend(ur)
            line.extend(ul)
            line.extend(ll)
            line.extend(ur)
            res.append(line)
            line = []
            line.extend(ll)
            line.extend(lr)
            line.extend(ur)
            line.extend(ll)
            res.append(line)

    with open(outfilename, "wb") as outputtxt:
        for line in res:
            np.savetxt(outputtxt, [np.array(line).flatten()])
    #output = open(binfilename, 'wb')

    #pickle.dump(vertices, output)
    #marshal.dump(np.array(vertices).tolist(), output)
    #output.close()
    return [minx, miny, maxx, maxy]

def calculate(buildingsfile, terrainfile, config):

    with open(buildingsfile) as f:
        buildings = None
        for l in f:
            inarr = np.genfromtxt(StringIO(l), delimiter=" ")
            for vec in np.split(inarr, len(inarr) / 3):
                if buildings is None:
                    buildings = [vec]
                else:
                    buildings = np.append(buildings, [vec], axis=0)

    if buildings is None and "borders" in list(config.keys()):
        minx = config["borders"][0]
        miny = config["borders"][1]
        maxx = config["borders"][2]
        maxy = config["borders"][3]
        minz = config["coverageLevel"]
        maxz = config["coverageMaxLevel"]
    else:
        minx = np.amin(buildings, axis=0)[0]
        miny = np.amin(buildings, axis=0)[1]
        minz = np.amin(buildings, axis=0)[2]
        maxx = np.amax(buildings, axis=0)[0]
        maxy = np.amax(buildings, axis=0)[1]
        maxz = np.amax(buildings, axis=0)[2]
        #print np.amax(buildings, axis=0)


    res = []
    line = []
    line.extend([maxx, maxy, minz])
    line.extend([minx, maxy, minz])
    line.extend([minx, miny, minz])
    line.extend([maxx, maxy, minz])
    res.append(line)
    line = []
    line.extend([minx, miny, minz])
    line.extend([maxx, miny, minz])
    line.extend([maxx, maxy, minz])
    line.extend([minx, miny, minz])
    res.append(line)

    with open(terrainfile, "wb") as outputtxt:
        for line in res:
            np.savetxt(outputtxt, [np.array(line).flatten()])

    #print minx, miny, minz, maxx, maxy, maxz
    return [minx, miny, maxx, maxy]


"""
if __name__ == "__main__":
    filename = sys.argv[1]
    outfilename = sys.argv[2]
    config = {"terrainHeight": 100,
              "terrainWidth": 20,
              "terrainLevel": "auto"}
    print calculate(filename, outfilename, config)
"""

