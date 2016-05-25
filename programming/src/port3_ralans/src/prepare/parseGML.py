
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
import sys

# infilename = "gml/westerberg.gml"
#outfilename = "faces/faceswb.txt"


def parse(infilename, outfilename):
    tree = etree.parse(infilename)
    names = {"core": "http://www.opengis.net/citygml/1.0", "tran": "http://www.opengis.net/citygml/transportation/1.0",
             "gml": "http://www.opengis.net/gml", "wtr": "http://www.opengis.net/citygml/waterbody/1.0",
             "xlink": "http://www.w3.org/1999/xlink", "grp": "http://www.opengis.net/citygml/cityobjectgroup/1.0",
             "luse": "http://www.opengis.net/citygml/landuse/1.0",
             "frn": "http://www.opengis.net/citygml/cityfurniture/1.0",
             "app": "http://www.opengis.net/citygml/appearance/1.0",
             "tex": "http://www.opengis.net/citygml/texturedsurface/1.0",
             "xal": "urn:oasis:names:tc:ciq:xsdschema:xAL:2.0", "bldg": "http://www.opengis.net/citygml/building/1.0",
             "dem": "http://www.opengis.net/citygml/relief/1.0", "veg": "http://www.opengis.net/citygml/vegetation/1.0",
             "gen": "http://www.opengis.net/citygml/generics/1.0"}
    r = tree.xpath('//gml:posList/text()', namespaces=names)
    with open(outfilename, "w") as outfile:
        for t in r:
            outfile.write(t + "\n")


if __name__ == "__main__":
    infilename = sys.argv[1]
    outfilename = sys.argv[2]
    parse(infilename, outfilename)


