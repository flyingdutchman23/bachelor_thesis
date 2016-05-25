
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

from .run import main
from .src.config import fConfigfiles, config as cfg
from copy import deepcopy as copy
from . import viewer1d, viewer2d, viewerCircleScattered
import sys

if __name__ == '__main__':

    try:
        viewer = sys.argv[1]
    except:
        viewer = False

    if not viewer:
        #Create list and line file
        line = '[-10,0,2] [10,0,2] 1'
        list = '[-10,0,2] [-5,0,2] [0,0,2] [5,0,2] [10,0,2] [0,2,2] [0,-2,2]'
        with open(fConfigfiles + 'line.rec', 'w') as f:
            f.write('1\n'+line)
        with open(fConfigfiles + 'list.rec', 'w') as f:
            f.write('4\n'+list)

        #Tests for 1d-Viewer
        main("inputfiles/small_street_flat.osm debugLevel=5 transmitters=[[-5,0,2]] receivers=configfiles/line.rec name=trPrecLineF", copy(cfg))

        #Tests for 2d-Viewer
        main("inputfiles/small_street_flat.osm transmitters=[[-5,0,2]] name=trPrecA1 debugLevel=5", copy(cfg))
        main("inputfiles/small_street_flat.osm transmitters=[[-5,0,2]] name=trPrecA2 coverageLevel=2 coverageMaxLevel=2 debugLevel=5", copy(cfg))
        main("inputfiles/small_street_flat.osm transmitters=[[-5,0,2]] name=trPrecC coverageLevel=1 coverageMaxLevel=3 debugLevel=5")
        main("inputfiles/small_street_flat.osm transmitters=area stepSize=10 name=trArecA10", copy(cfg))
        main("inputfiles/small_street_flat.osm transmitters=area stepSize=10 name=trArecC10 coverageLevel=1 coverageMaxLevel=12", copy(cfg))

        #Tests for Scattered-Viewer
        main("inputfiles/small_street_flat.osm debugLevel=5 transmitters=[[-5,0,2]] receivers=[[-10,0,2],[-5,0,2],[0,0,2],[5,0,2],[10,0,2],[0,2,2],[0,-2,2]] name=trPrecListM", copy(cfg))
        main("inputfiles/small_street_flat.osm debugLevel=5 transmitters=[[-5,0,2]] receivers=configfiles/list.rec name=trPrecListF", copy(cfg))
        main("inputfiles/small_street_flat.osm debugLevel=5 transmitters=[[-5,0,2]] receivers=street name=trPrecS coverageLevel=2 coverageMaxLevel=2", copy(cfg))
    else:


        #Open Viewer
        viewer1d.main('outputfiles/small_street_flat_trPrecLineF.zip l')
        viewer2d.main('outputfiles/small_street_flat_trPrecA1.zip')
        viewer2d.main('outputfiles/small_street_flat_trPrecA2.zip')
        viewer2d.main('outputfiles/small_street_flat_trPrecA1.zip outputfiles/small_street_flat_trPrecA2.zip')
        viewer2d.main('outputfiles/small_street_flat_trPrecA1.zip [-5,0,2] 2 outputfiles/small_street_flat_trPrecA2.zip [-2,0,1] 5')
        viewer2d.main('outputfiles/small_street_flat_trArecA10.zip')
        viewer2d.main('outputfiles/small_street_flat_trArecA10.zip [-2,2,1] 5')
        viewer2d.main('outputfiles/small_street_flat_trArecC10.zip')
        viewer2d.main('outputfiles/small_street_flat_trArecC10.zip [-2,2,1] 1')
        viewer2d.main('outputfiles/small_street_flat_trArecC10.zip [-2,2,1] 2')
        viewer2d.main('outputfiles/small_street_flat_trArecC10.zip [-2,2,1] 1 outputfiles/small_street_flat_trArecC10.zip [-2,2,1] 2')
        viewerCircleScattered.main('outputfiles/small_street_flat_trPrecListM.zip -b')
        viewerCircleScattered.main('outputfiles/small_street_flat_trPrecListF.zip -b')
        viewerCircleScattered.main('outputfiles/small_street_flat_trPrecS.zip -b')
