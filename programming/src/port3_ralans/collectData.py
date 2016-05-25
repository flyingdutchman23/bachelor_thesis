
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

import sys
from .src.config import *
from .src.launcher import prepare4ns3
from .src.launcher import makeViewable
from .src.prepare import extractEdges
from .src.util.functions import saveAsZip, saveViewerConfig
import pickle as pickle

def collect(cfg):

    try:
        with open(cfg) as f:
            cfg = pickle.load(f)
    except OSError as e:
        print(e)
        sys.exit()

    files = cfg['files']
    identifier = files['identifier']
    coveragefolder = files['coveragefolder']
    ns3filename = files['ns3filename']
    buildingsedgesfilename = files['buildingsedgesfilename']
    buildingsedgesbinfilename = files['buildingsedgesbinfilename']
    terrainedgesfilename = files['terrainedgesfilename']
    terrainedgesbinfilename = files['terrainedgesbinfilename']
    rayfolder = files['rayfolder']
    workfolder = fTmp + identifier + '/'


    # prepare for ns-3
    print("Preparing data for ns-3...")
    prepare4ns3.prepare4ns3(coveragefolder, ns3filename, cfg['borders'], cfg)
    print("...finished")
    if (cfg["debugLevel"]) >= 3:
        if cfg['preprop']:
            extractEdges.toBin(buildingsedgesfilename, buildingsedgesbinfilename)
            extractEdges.toBin(terrainedgesfilename, terrainedgesbinfilename)

    if cfg["debugRays"] is True:
        transmitters = cfg["transmitters"]
        if cfg["clusterArray"] is not None:
            x,y = cfg["clusterArray"].split("_")
            transmitters = transmitters[x:y]
        for transmitter in transmitters:
            x, y, z = transmitter
            string = "[{0:g}, {1:g}, {2:g}].txt".format(x, y, z)
            rayfilename = rayfolder + string
            raybinfilename = rayfilename[:-3] + "bin"
            makeViewable.makeViewable(rayfilename, raybinfilename)
            if cfg['debugLevel'] == 5: print("Make file: " + str(rayfilename) + "viewable")

    # generate zip with results
    print("generating viewerconfig")
    saveViewerConfig(identifier, cfg)

    print("generating zipfile")
    saveAsZip(identifier, workfolder, cfg['debugLevel'], cfg["debugRays"])


    print("Finished.")



if __name__ == "__main__":
    collect(sys.argv[1])
