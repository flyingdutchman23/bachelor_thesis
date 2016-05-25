
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
from lxml import etree
from io import StringIO
import numpy as np
import sys

import utm


#osmfile = "osm/westerberg.osm"
#polyfile = "faces/osmpoly.txt"



SIGMA = 1e-10


def writePoly(outfile, poly):
    polystr = ""
    for p in poly:
        polystr += str(p) + " "
    polystr = polystr[:-1]
    polystr += "\n"
    outfile.write(polystr)


def reversePoly(poly):
    newpoly = np.array([])
    for i in range(len(poly) - 3, -1, -3):
        newpoly = np.append(newpoly, poly[i])
        newpoly = np.append(newpoly, poly[i + 1])
        newpoly = np.append(newpoly, poly[i + 2])
    return newpoly


def parse(osmfile, polyfile, wayfile, config):
    groundheight = config["groundHeight"]
    buildingheight = config["buildingHeight"]

    tree = etree.parse(osmfile)

    #print "parsed into etree"

    #first the nodes:
    r = tree.findall("node")

    #print "found nodes"

    nodes = {}
    for node in r:
        key = node.xpath("./attribute::id")[0]
        #higher values
        #lat = float(node.xpath("./attribute::lat")[0])*10000
        #lon = -float(node.xpath("./attribute::lon")[0])*10000
        #conversion degrees->UTM
        utm_tuple = utm.from_latlon(float(node.xpath("./attribute::lat")[0]), float(node.xpath("./attribute::lon")[0]))
        #nodes[key] = (utm_tuple[1], utm_tuple[0])
        nodes[key] = (utm_tuple[0], utm_tuple[1])

    #now the buildings:
    r = tree.findall('//way')

    #print "nodes extracted"

    buildings=[]
    ways=[]
    for nd in r:
        if len(nd.xpath("./tag[@k='building']")) == 1 or len(nd.xpath("./tag[@k='building:part']")) == 1:
            buildings.append(nd)
        if len(nd.xpath("./tag[@k='highway']")) == 1 or len(nd.xpath("./tag[@k='highway:part']")) == 1:
            ways.append(nd)

    for rel in tree.findall('//relation') :
        if len(rel.xpath("./tag[@k='building']")) == 1:
            for member in rel.xpath("./member[@type='way' and @role='outer']") :
                building = tree.find("//way[@id='"+member.get("ref")+"']")
                if building is None:
                    print("B ID with None:", member.get("ref"))
                else:
                    buildings.append(building)
        if len(rel.xpath("./tag[@k='highway']")) == 1:
            for member in rel.xpath("./member[@type='way' and @role='outer']") :
                way = tree.find("//way[@id='"+member.get("ref")+"']")
                if way is None:
                    print("ID with None:", member.get("ref"))
                else:
                    ways.append(way)

    rawbuildings = []
    rawstreets = []
    with open(wayfile, "w") as woutfile:
        with open(polyfile, "w") as boutfile:
            for way in ways:
                polynodekeys = way.xpath('./nd/attribute::ref')
                poly = np.array([])
                for k in polynodekeys:
                    poly = np.append(poly, nodes[k][0])
                    poly = np.append(poly, nodes[k][1])
                    poly = np.append(poly, 0)

                writePoly(woutfile, poly)
                rawstreets.append(poly.tolist())

            for building in buildings:
                polynodekeys = building.xpath('./nd/attribute::ref')
                poly = np.array([])
                for k in polynodekeys:
                    poly = np.append(poly, nodes[k][0])
                    poly = np.append(poly, nodes[k][1])
                    poly = np.append(poly, groundheight)

                #repeat first vertex:
                if np.linalg.norm(poly[:3] - poly[-3:]) > SIGMA:
                    #poly.extend(poly[:3])
                    poly = np.append(poly, poly[:3])

                #is it ccw or cw? - http://debian.fmi.uni-sofia.bg/~sergei/cgsr/docs/clockwise.htm
                pos = 0
                neg = 0
                for i in range(1, len(poly) / 3 - 1):
                    a = poly[(i - 1) * 3:i * 3]
                    b = poly[i * 3:(i + 1) * 3]
                    c = poly[(i + 1) * 3:(i + 2) * 3]
                    if np.cross(a - b, c - b)[2] > 0:
                        pos += 1
                    else:
                        neg += 1

                    #change orientation if needed:
                if pos < neg:
                    poly = reversePoly(poly)
                writePoly(boutfile, poly)  #ground
                rawbuildings.append(poly.tolist())

                roofPoly = poly + np.tile([0, 0, buildingheight], len(poly) / 3)
                for i in range(0, len(poly) / 3 - 1):
                    wallPoly = []
                    wallPoly.extend(poly[i * 3:(i + 1) * 3])  #lower left
                    wallPoly.extend(roofPoly[i * 3:(i + 1) * 3])  #upper left
                    wallPoly.extend(roofPoly[(i + 1) * 3:(i + 2) * 3])  #upper right
                    wallPoly.extend(poly[(i + 1) * 3:(i + 2) * 3])  #lower right
                    wallPoly.extend(poly[i * 3:(i + 1) * 3])  #lower left
                    writePoly(boutfile, wallPoly)
                    rawbuildings.append(wallPoly)
                roofPoly = reversePoly(roofPoly)
                writePoly(boutfile, roofPoly)
                rawbuildings.append(roofPoly.tolist())

    return rawbuildings, rawstreets


if __name__ == "__main__":
    osmfile = sys.argv[1]
    polyfile = sys.argv[2]
    wayfile = sys.argv[3]

    config = {"groundHeight": 0,
              "buildingHeight": 10}

    parse(osmfile, polyfile, wayfile, config)

#
#for t in r :
#	outfile.write(t+"\n")
