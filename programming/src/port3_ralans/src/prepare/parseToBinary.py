
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

# filename="faces/osmpoly.txt"
#binfilename="pickle/osmpoly.pickle"



SIGMA = 1e-10


def triangulate(polygon):
    """
    simple triangulation using triangle_fan scheme (see OpenGL documentation) -  the result is not valid for concave polygons
    """
    inarr = polygon
    outarr = []
    for i in range(1, len(inarr) / 3):
        if (i + 2) * 3 <= len(inarr):
            a = inarr[0:3]
            b = inarr[i * 3:(i + 1) * 3]
            c = inarr[(i + 1) * 3:(i + 2) * 3]
            gl.logger.debug(str(a) + " " + str(b) + " " + str(c))
            #fix: avoid nan by ignoring duplicates
            debugmes = np.sum((b - c) * (b - c)), np.sum((a - b) * (a - b)), np.sum((a - c) * (a - c))
            gl.logger.debug( str(debugmes))
            if np.sum((b - c) * (b - c)) > SIGMA and np.sum((a - b) * (a - b)) > SIGMA and np.sum(
                            (a - c) * (a - c)) > SIGMA:
                gl.logger.debug("is tri")
                outarr = pushTriangle(a, b, c, outarr)
            else:
                gl.logger.debug( "is no tri" )
    return outarr


def triangulate2(polygon):
    """
    more advanced algorithm for triangulation of a polygon - also functioning with concave polygons
    ears are found and removed (see http://en.wikipedia.org/wiki/Polygon_triangulation)
    """
    outarr = []
    #repeat first vector if this isn't the case, yet
    if np.linalg.norm(polygon[:3] - polygon[-3:]) > SIGMA:
        polygon = polygon.tolist()
        polygon.extend(polygon[:3])
        polygon = np.array(polygon)
    found = True
    #remove ears:
    while len(polygon) > 12 and found:
        assert len(polygon) % 3 == 0
        #print len(polygon)
        found = False
        #find ear:
        for i in range(1, len(polygon) / 3 - 1):
            a = polygon[(i - 1) * 3:i * 3]
            b = polygon[i * 3:(i + 1) * 3]
            c = polygon[(i + 1) * 3:(i + 2) * 3]
            #print len(a), len(b),len(c)

            #found ear:
            if inPolygon(a, c, polygon):
                polygon = np.append(polygon[:i * 3], polygon[(i + 1) * 3:])  #remove ear
                #push triangle:
                outarr = pushTriangle(a, b, c, outarr)
                #print "found ear"
                found = True
                break
    if not found:
        gl.logger.warning("did not terminate: " + str(len(polygon)))
        gl.logger.warning(str(polygon))
    outarr = pushTriangle(polygon[0:3], polygon[3:6], polygon[6:9], outarr)
    return outarr

def getTriangulatedNormal(polygon):

    found = True
    while len(polygon) > 12 and found:
        assert len(polygon) % 3 == 0

        found = False
        for i in range(1, len(polygon) / 3 - 1):
            a = polygon[(i - 1) * 3:i * 3]
            b = polygon[i * 3:(i + 1) * 3]
            c = polygon[(i + 1) * 3:(i + 2) * 3]

            if inPolygon(a, c, polygon):
                return np.cross(a - b, c - b)
    return np.cross(polygon[0:3] - polygon[3:6], polygon[6:9] -  polygon[3:6])


def inPolygon(a, b, polygon):
    """
    checks if a line from a to b lies completely within the polygon
    """
    #print "checking",a,b,polygon
    #if the center isn't in the polygon, it's impossible, that the whole line is in the polygon
    if countRayCrossings((a + b) / 2, [100000, -100000, 100000], polygon) % 2 != 1:
        #print "by center"
        return False
    #if the line intersects with any of the polygon's sides, it can't be completely in the polygon either
    if countRayCrossings(a, b, polygon) != 0:
        #print "by crossings"
        return False

    return True


def countRayCrossings(a, b, polygon):
    """
    This algorithm determines the number of intersections of a line from a to b with the polygon.
    """
    #The check is performed in only two dimensions, this is allowed because the projection doesn't change the topology.
    #A valid projection is determined by just trying it with xy, the xz and the yz plane.
    res = countRayCrossings2D(a, b, polygon, 0, 1)
    if res < 0:
        res = countRayCrossings2D(a, b, polygon, 0, 2)
        if res < 0:
            res = countRayCrossings2D(a, b, polygon, 1, 2)
            if res < 0:
                gl.logger.warning("something went wrong - inPolygon-check failed in all projections")
                gl.logger.warning(str(polygon))
                return 0
    return res

def countRayCrossings2D(a, b, polygon, dim1, dim2):
    """
    This algorithm determines the number of intersections of a line from a to b with the polygon, where dim1 and dim2 denote a 2d-projection.
    """
    count = 0
    for i in range(1, len(polygon)/3):

        c = polygon[(i-1)*3:i*3]
        d = polygon[i*3:(i+1)*3]

        if (b[dim1]-a[dim1]) == 0 or ((d[dim1]-c[dim1])*(b[dim2]-a[dim2])/(b[dim1]-a[dim1])-d[dim2]+c[dim2]) == 0:
            return -1

        tau =   (  c[dim2] - a[dim2]  - (c[dim1] - a[dim1]) * (b[dim2] - a[dim2]) / (b[dim1] - a[dim1]) ) /\
                ( (d[dim1] - c[dim1]) * (b[dim2] - a[dim2]) / (b[dim1] - a[dim1]) -  d[dim2] + c[dim2]  )
        lamda = (  c[dim1] + tau * (d[dim1] - c[dim1]) - a[dim1]) / (b[dim1] - a[dim1])

        if (SIGMA < tau < 1 - SIGMA and 0 <= lamda <= 1) or (SIGMA < lamda < 1 - SIGMA and 0 <= tau <= 1):
            count += 1

    return count


def pushTriangle(a, b, c, arr):
    """
    Add vertices and normals of a triangle described by a,b,c to arr.
    """
    #print a,b,c
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


def parse(filename, binfilename):
    gl.logger.debug("parsing file to binary: "+ filename)
    vertices = []
    with open(filename) as f:
        for l in f:
            #print "new polygon"
            inarr = np.genfromtxt(StringIO(l), delimiter=" ")

            #print "next:"

            #remove offset to avoid floating precision problems
            #inarr = inarr - np.tile(center,len(inarr)/3)
            vertices.extend(triangulate2(inarr))
    with open(binfilename, 'wb') as output:
    #pickle.dump(vertices, output)
        marshal.dump(np.array(vertices).tolist(), output)

if __name__ == "__main__":
    print("parsing...")


    filename = sys.argv[1]
    binfilename = sys.argv[2]
    parse(filename, binfilename)


