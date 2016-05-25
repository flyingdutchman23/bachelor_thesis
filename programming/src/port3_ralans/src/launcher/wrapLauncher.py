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
import subprocess
import time
import datetime
import sys
import pp

from src import globals as gl


def createTypeString(cfg):

    POINT = 0
    LINE = 1
    AREA = 2
    CUBIC = 3
    LIST = 4

    type = cfg["receiverType"]
    minx = cfg["borders"][0]
    maxx = cfg["borders"][2]
    miny = cfg["borders"][1]
    maxy = cfg["borders"][3]
    step = cfg["stepSize"]
    minz = cfg["coverageLevel"]
    maxz = cfg["coverageMaxLevel"]
    sx = sy = sz = step


    if type == POINT:
        px = cfg["receivers"][0][0]
        py = cfg["receivers"][0][1]
        pz = cfg["receivers"][0][2]
        return str(POINT) + " " + str(px) + " " + str(py) + " " + str(pz)

    elif type == LINE:
        line = cfg["receivers"][0]
        start, end, step = line
        return str(LINE) + " " + str(start[0]) + " " + str(start[1]) + " " + str(start[2]) + " " + str(end[0]) + " " + str(end[1]) + " " + str(end[2]) + " " + str(step)

    elif type == AREA:
        return str(AREA) + " " + str(minx) + " " + str(miny) + " " + str(maxx) + " " + str(maxy) + " " + str(minz) + " " + str(sx) + " " + str(sy)

    elif type == CUBIC:
        return str(CUBIC) + " " + str(minx) + " " + str(miny) + " " + str(minz) + " " + str(maxx) + " " + str(maxy) + " " + str(maxz) + " " + str(sx) + " " + str(sy) + " " + str(sz)
    elif type == LIST:
        receivers = cfg["receivers"]
        out = str(LIST)
        out += " " + str(len(receivers))
        for receiver in receivers:
            out += " " + str(receiver[0]) + " " + str(receiver[1]) + " " + str(receiver[2])
        return out


    else:
        print("unsupported type")
        sys.exit(-1)


def calculateTransmitterParallel(workFolder, cfg, transmitterSize):

    if cfg["preprop"]:
        gl.logger.info("extracting edges")
        try:
            blub = subprocess.check_output(['src/launcher/edges', workFolder],stderr=subprocess.STDOUT)
            gl.logger.debug("Cout Edges: " + str(blub))
        except subprocess.CalledProcessError as e:
            print("failed to extract edges, see logfile for further information")
            gl.logger.error(str(e))
            sys.exit(-1)
        gl.logger.info("... extracted")

    print("Starting launcher")
    now = datetime.datetime.now()
    gl.logger.info( "starting at " + str(now.hour) + ":" + str(now.minute) + ":" + str(now.second))
    oldtime = time.time()

    typeString = createTypeString(cfg)
    typeString = str(typeString if int(typeString[0]) not in [1,4] else typeString[0])
    gl.logger.debug("Typestring: " + typeString)


    job_server = pp.Server(secret="rjn8809nesjn")
    jobs = []

    for trid in range(0, transmitterSize):
        jobs.append(job_server.submit(calculateSingle, (cfg, trid, workFolder, typeString), (), ("subprocess",)))

    for i, job in enumerate(jobs):
        result = job()
        gl.logger.debug("Launcher-Cout for transmitterid " + str(i) + ": " + str(result))

    job_server.destroy()

    now = datetime.datetime.now()
    gl.logger.info("finishing at " + str(now.hour) + ":" + str(now.minute) + ":" + str(now.second))
    gl.logger.info("finished in " +  str(time.time() - oldtime) + " seconds")



def calculateSingle(cfg, trid, workFolder, typeString):

    try:
        blub = subprocess.check_output(
            ['src/launcher/launcher', workFolder, typeString, str(trid),
                str(cfg["rayNumber"]),
                str(cfg["maxIterations"]),
                str(cfg["receiveThreshold"]),
                str(cfg["diffractionThreshold"]),
                str(cfg["reflectionPart"]),
                str(cfg["wavelength"]),
                str(int(cfg["interference"])),
                str(cfg["maxRange"]),
                str(int(cfg["debugRays"])),
                str(int(cfg["debugLevel"])),
                str(cfg["deadDistance"]),
                str(cfg["scatteringPart"]),
                str(cfg["timeout"])],
            stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        blub = "Error: " + e.output

    return blub
