
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
import os
import sys

sys.path.append('src/util')
import shutil
from .src.util.networking import *
import marshal
from .src.launcher import wrapLauncher
from . import build_native
import socket
from . import src.globals as gl
import logging
from .src.config import *
from .src.util.functions import *

def main(port = None):
    print("PORT:", port)
    build_native.build()

    hostname = socket.gethostname()
    print("Start Server...")
    sock, conn = startLinkServer(port)
    print("Receive config")
    config = marshal.loads(receive(conn))
    print(" ...success")

    identifier = createIdentifier(config)

    workfolder = fTmp + hostname + '/' + identifier + '/'

    if config["preprop"]:
        gl.rmdir(workfolder)
    gl.mkdir(workfolder)
    gl.mkdir(workfolder + fPolygons)
    gl.mkdir(workfolder + fEdges)
    gl.mkdir(workfolder + fRays)
    gl.mkdir(workfolder + fLogs)
    gl.mkdir(fInputfiles)
    gl.mkdir(fConfigfiles)
    gl.mkdir(fOutputfiles)

    gl.initLogger(workfolder + fLogs, identifier, config["debugLevel"])

    buildingspolyfilename = workfolder + fPolygons + fileBuildings
    streetspolyfilename   = workfolder + fPolygons + fileStreets
    terrainpolyfilename   = workfolder + fPolygons + fileTerrain
    receiverfile = workfolder + "receivers.cfg"
    transmitterfile = workfolder + "transmitters.cfg"
    coveragefolder = workfolder + fCoverage
    rayfolder = workfolder + fRays

    gl.rmdir(coveragefolder)
    gl.mkdir(coveragefolder)


    # receive all required data:
    gl.logger.info("Receiving required data")
    for filename in [buildingspolyfilename, streetspolyfilename, terrainpolyfilename]:
        data = receive(conn)
        f = open(filename, "wb")
        f.write(data)
        f.close()
    transmitters = marshal.loads(receive(conn))
    if config["receiverType"] == 4:
        data = receive(conn)
        f = open(receiverfile, "wb")
        f.write(data)
        f.close()

    conn.close()
    sock.close()
    gl.logger.info("\t ...data received.")

    #do simulation:
    gl.logger.info("starting simulation")

    # do own part of calculation
    savePositions4Launcher(transmitters, transmitterfile)
    wrapLauncher.calculateTransmitterParallel(workfolder, config, len(transmitters))

    gl.logger.info("Sending calculated data...")
    #send generated data:
    sock, conn = startLinkServer()
    send(hostname, conn)
    for transmitter in transmitters:
        x,y,z = transmitter
        transmitter = "[{0:g}, {1:g}, {2:g}]".format(x,y,z)
        f = open(coveragefolder + str(transmitter) + '.txt', 'r')
        data = f.read()
        send(data, conn)
        f.close()
        if config["debugRays"] is True:
            f = open(rayfolder + str(transmitter) + '.txt', 'r')
            data = f.read()
            send(data, conn)
            f.close()

    for file in [logEdge, logScript, logLauncher]:
        with open(workfolder + fLogs + file, 'r') as f:
            send(f.read(), conn)

    conn.close()
    sock.close()
    print("Finished")



if __name__ == "__main__":

    port = None
    try:
        port = int(sys.argv[1])
    except:
        print("Invalid Port, using default Port ", TCP_PORT)
    print("Port:", port)
    main(port)





