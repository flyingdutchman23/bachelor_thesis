
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
from io import StringIO


import src.globals as gl
from src.util import geometryHelper

EPSILON = 0.0000001


def toBin(edgefilename, edgebinfilename):
    edges = []
    with open(edgefilename) as f:

        for l in f:
            inarr = np.genfromtxt(StringIO(l), delimiter=" ")
            edge = [(inarr[0], inarr[1], inarr[2]), (inarr[3], inarr[4], inarr[5]), ]
            edges.append(edge)

    vertices = []
    for edge in edges:
        color = [1, 0, 0]
        vertices.extend(edge[0])
        vertices.extend(color)
        vertices.extend(edge[1])
        vertices.extend(color)
    vertices = (np.array(vertices)).tolist()
    with open(edgebinfilename, 'wb') as output:
        marshal.dump(vertices, output)

def extract(polygonfilename, edgefilename, edgebinfilename = None):
    """
    acc=None
    for l in f:
        inarr = np.genfromtxt(StringIO(l), delimiter=" ")
        if acc is None :
            acc=[inarr[0:3]]
        else :
            acc=np.append(acc,[inarr[0:3]],axis=0)
    """

    # print acc
    #center=np.mean(acc,axis=0)
    polygons = []
    with open(polygonfilename) as f:
        for l in f:
            #print "new polygon"
            inarr = np.genfromtxt(StringIO(l), delimiter=" ")

            #print "next:"

            #remove offset to avoid floating precision problems
            #inarr = inarr - np.tile(center,len(inarr)/3)
            polygons.append(inarr)
    gl.logger.debug("polygons: " + str(len(polygons)))
    edges = []

    for polyi in range(len(polygons)):
        poly = polygons[polyi]
        for i in range(len(poly) / 3 - 1):
            e1 = np.array(poly[i * 3:(i + 1) * 3])
            e2 = np.array(poly[(i + 1) * 3:(i + 2) * 3])
            #edges.append((e1.tolist(),e2.tolist()))


            #find neigbouring edge:
            edgeidentified = False
            for poly2i in range(polyi + 1, len(polygons)):
                poly2 = polygons[poly2i]
                for j in range(len(poly2) / 3 - 1):
                    eb1 = np.array(poly2[j * 3:(j + 1) * 3])
                    eb2 = np.array(poly2[(j + 1) * 3:(j + 2) * 3])
                    #if (np.dot(eb1-e1,eb1-e1) < EPSILON and np.dot(eb2-e2,eb2-e2) < EPSILON) or (np.dot(eb2-e1,eb2-e1) < EPSILON and np.dot(eb1-e2,eb1-e2)<EPSILON) :
                    if (np.dot(eb1 - e1, eb1 - e1) == 0 and np.dot(eb2 - e2, eb2 - e2) == 0) or (
                            np.dot(eb2 - e1, eb2 - e1) == 0 and np.dot(eb1 - e2, eb1 - e2) == 0):
                        n1 = geometryHelper.getNormal(poly)
                        n2 = geometryHelper.getNormal(poly2)

                        if np.dot(n1, n2) < 0.95:  #only if faces do not point in same direction
                            p = (e1 + e2) / 2 + (n1 + n2) * 0.01

                            if geometryHelper.getIntersection(p, -n1, poly ) is None and \
                               geometryHelper.getIntersection(p, -n2, poly2) is None:
                                edges.append((e1.tolist(), e2.tolist(), n1.tolist(), n2.tolist()))
                                edgeidentified = True
                if edgeidentified:
                    break

    gl.logger.debug("edges found: " + str(len(edges)))

    with open(edgefilename, "wb") as outputtxt:
        for edge in edges:
            np.savetxt(outputtxt, [np.array(edge).flatten()])

    """
    output = open("../3dviewer/bin/edges.bin", 'wb')
    marshal.dump(edges, output)
    output.close()
    """

    if edgebinfilename is not None:
        vertices = []
        for edge in edges:
            color = [1, 0, 0]
            vertices.extend(edge[0])
            vertices.extend(color)
            vertices.extend(edge[1])
            vertices.extend(color)
        vertices = (np.array(vertices)).tolist()
        with open(edgebinfilename, 'wb') as output:
            marshal.dump(vertices, output)


"""
if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise "Invalid amount of commandline arguments"
    polygonfilename = sys.agv[0]
    edgefilename = sys.agv[1]
    edgebinfilename = sys.agv[2]
    extract(polygonfilename, edgefilename, edgebinfilename)
"""
