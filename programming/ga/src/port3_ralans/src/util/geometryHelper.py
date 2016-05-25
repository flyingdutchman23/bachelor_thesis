
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

import sys
sys.path.append('./')
from src.prepare import parseToBinary

SIGMA = 0.000001


def countRayCrossings(a, b, polygon):
    """
    This algorithm determines the number of intersections of a line from a to b with the polygon.
    """

    # The check is performed in only two dimensions, this is allowed because the projection doesn't change the topology.
    #A valid projection is determined by just trying it with xy, the xz and the yz plane.
    try:
        return countRayCrossings2D(a, b, polygon, 0, 1)
    except:
        try:
            return countRayCrossings2D(a, b, polygon, 0, 2)
        except:
            try:
                return countRayCrossings2D(a, b, polygon, 1, 2)
            except:
                print("something went wrong - inPolygon-check failed in all projections")
                return 0


def countRayCrossings2D(a, b, polygon, dim1, dim2):
    """
    This algorithm determines the number of intersections of a line from a to b with the polygon, where dim1 and dim2 denote a 2d-projection.
    """
    count = 0
    for i in range(1, len(polygon) / 3):
        c = polygon[(i - 1) * 3:i * 3]
        d = polygon[i * 3:(i + 1) * 3]
        tau = 2
        lamda = 2
        # print "check crossing:", a,b,c,d,dim1,dim2
        #calculation of intersection according to i=a+lambda*(b-a)=c+tau*(d-c) with reduction to 2 dimesnions (this keeps the topology)

        tau =   (c[dim2] - a[dim2]  - (c[dim1] - a[dim1]) * (b[dim2] - a[dim2]) / (b[dim1] - a[dim1]) ) / \
              ( (d[dim1] - c[dim1]) * (b[dim2] - a[dim2]) / (b[dim1] - a[dim1]) -  d[dim2] + c[dim2] )
        lamda = (c[dim1] + tau * (d[dim1] - c[dim1]) - a[dim1]) / (b[dim1] - a[dim1])
        assert tau == tau
        assert lamda == lamda
        #print tau, lamda
        if tau > SIGMA and tau < 1 - SIGMA and lamda >= 0 and lamda <= 1 or lamda > SIGMA and lamda < 1 - SIGMA and tau >= 0 and tau <= 1:
            count += 1
        #if lamda > SIGMA and lamda < 1-SIGMA and tau >= SIGMA and tau <= 1+SIGMA:
        #	count += 1
    return count


def getIntersection(origin, direction, polygon):
    """
    This algorithm determines the intersection of a ray with a polygon. Or None if there is no intersection.
    """
    p1 = polygon[0:3]
    p2 = polygon[3:6]
    p3 = polygon[6:9]

    #n = np.cross(p1 - p2, p3 - p2)  # normal of polygon
    #n /= np.linalg.norm(n)
    n = parseToBinary.getTriangulatedNormal(polygon)

    d = np.dot(n, p1)

    if np.dot(direction, n) == 0:  # catch: ray parallel to face
        return None

    lamda = (d - np.dot(origin, n)) / np.dot(direction, n)
    if lamda <= 0:
        return None

    intersect = origin + lamda * direction  # calculate intersection
    if countRayCrossings(intersect, [100000, 100000, 100000],
                         polygon) % 2 == 0:  # see if the intersection is within the polygon
        return None

    return (intersect, n)


def getPolygons(filename):
    polygons = []
    with open(filename) as f:
        for l in f:
            inarr = np.genfromtxt(StringIO(l), delimiter=" ")
            polygons.append(inarr)
    return polygons


def inBuilding(a, polygons):
    crossings = 0
    for polygon in polygons:
        if (getIntersection(a, np.array([0, 0, 1]), polygon) is not None):
            crossings += 1
    if crossings % 2 == 0:
        return False
    else:
        return True


def getNormal(polygon):

    """
    Returns the normal of a polygon (convex & concave polygons supported)
    TODO: find where this algorithm is from!
    """

    polytmp = np.array(polygon)  # make sure we work on a copy, and it's numpy format
    # repeat first if necessary
    if np.linalg.norm(polytmp[:3] - polytmp[-3:]) > SIGMA:
        polytmp = polytmp.tolist()
        polytmp.extend(polytmp[:3])
        polytmp = np.array(polytmp)
    #repeat second
    polytmp = np.append(polytmp, polytmp[3:6])
    n = -np.cross(polytmp[:3] - polytmp[3:6], polytmp[6:9] - polytmp[3:6])
    votesfor = 1
    votesagainst = 0

    for corneri in range(1, len(polytmp) / 3 - 2):
        p1 = polytmp[3 * corneri:3 * (corneri + 1)]
        p2 = polytmp[3 * (corneri + 1):3 * (corneri + 2)]
        p3 = polytmp[3 * (corneri + 2):3 * (corneri + 3)]
        n2 = -np.cross(p1 - p2, p3 - p2)
        if np.dot(n, n2) > 0:
            votesfor += 1
        else:
            votesagainst += 1
    if votesagainst > votesfor:
        n *= -1
    n /= np.linalg.norm(n)
    return n

    #normal = parseToBinary.getTriangulatedNormal(polygon)
    #normal /= np.linalg.norm(normal)
    #return normal

if __name__ == "__main__":
    polygons = getPolygons("../3dviewer/faces/simpleOSM_reduced.txt")
    print(inBuilding(np.array([0, 10, 0]), polygons))
	
