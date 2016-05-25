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
import sys

sys.path.append('src/util')
from .src.prepare import calculateTerrain
from .src.prepare import parseToBinary
from .src.prepare import parseOSM
from .src.prepare import parseGML
from .src.prepare import removeOffset
from .src.prepare import extractEdges
from .src.util.functions import *
from .src.config import *
from .src.config import config as defaultconfig
from .src.util import networking
from .src.launcher import wrapLauncher
from .src.launcher import prepare4ns3
from .src.launcher import makeViewable
import marshal
from . import build_native
import time
import datetime
from .src import globals as gl
import numpy as np
import os
import socket

USAGE = "Usage: python run.py -g | mapfile [configfile] [transmitterfile] [receiverfile] [param=...] [name=...] [-m]"


def main(command=None, cfg=defaultconfig, build=False, mapOnly=False):


    # C-Launcher is finished, there is no need to compile it every time
    if build:
        print("Compiling C++-Launcher")
        build_native.build()

    st = time.time()

    # parse programparams
    cfg, mapParsed = parseCommand(cfg, command)
    if cfg["name"] == "mapOnly":
        mapOnly = True

    # update config dicitonary
    workfolder, inputmap, inputtype, configfilename, receiverfile, identifier, cfg = setConfig(cfg)

    # parse mapfiles if needed
    if not mapParsed:
        cfg = parseMap(workfolder, inputmap, inputtype, cfg, configfilename, mapOnly)
    else:
        cfg = copyInputFiles(sys.argv[1], workfolder, cfg, configfilename)
    borders = cfg["borders"]


    buildingsedgesfilename = workfolder + fEdges + fileBuildings
    buildingsedgesbinfilename = workfolder + fEdges + binBuildings
    terrainedgesfilename = workfolder + fEdges + fileTerrain
    terrainedgesbinfilename = workfolder + fEdges + binTerrain
    rayfolder = workfolder + fRays
    coveragefolder = workfolder + fCoverage

    streetspolyfilename = workfolder + fPolygons + fileStreets
    buildingspolyfilename = workfolder + fPolygons + fileBuildings
    terrainpolyfilename = workfolder + fPolygons + fileTerrain

    # raycaster
    gl.rmdir(coveragefolder)
    gl.mkdir(coveragefolder)


    # generate transmitter list if coverage required
    if cfg["transmitters"] == "area":
        cfg["transmitters"] = []
        for y in frange(borders[1], borders[3], cfg["stepSize"]):
            for x in frange(borders[0], borders[2], cfg["stepSize"]):
                cfg["transmitters"].append([x, y, cfg["coverageLevel"]])
    elif cfg["transmitters"] == "cubic":
        cfg["transmitters"] = []
        for z in frange(cfg["coverageLevel"], cfg["coverageMaxLevel"], cfg["stepSize"]):
            for y in frange(borders[1], borders[3], cfg["stepSize"]):
                for x in frange(borders[0], borders[2], cfg["stepSize"]):
                    cfg["transmitters"].append([x, y, z])

    elif cfg["transmitters"] == "street":
        cfg["transmitters"] = calculatePositionFromStreet(streetspolyfilename, cfg["stepSize"],
                                                          cfg["transmitterHeight"])

    transmitterfile = workfolder + 'transmitters.cfg'
    savePositions4Launcher(cfg["transmitters"], transmitterfile)

    # generate receiver list if type is street
    if cfg["receivers"] == "street":
        cfg["receivers"] = calculatePositionFromStreet(streetspolyfilename, cfg["stepSize"],
                                                       cfg["coverageLevel"])
        savePositions4Launcher(cfg["receivers"], receiverfile)
        cfg["receiverType"] = 4

    gl.logger.info("starting simulation")

    if cfg["cluster"]:

        spawnJobs(cfg, workfolder)

        # save some filenames and the config dictionary
        picklefile = workfolder + identifier + ".dump"
        files = {
            'identifier': identifier,
            'coveragefolder': coveragefolder,
            'ns3filename': fOutputfiles + identifier + ".txt",
            'buildingsedgesfilename': buildingsedgesfilename,
            'buildingsedgesbinfilename': buildingsedgesbinfilename,
            'terrainedgesfilename': terrainedgesfilename,
            'terrainedgesbinfilename': terrainedgesbinfilename,
            'rayfolder': rayfolder
        }
        cfg['files'] = files
        import pickle

        with open(picklefile, "w") as f:
            pickle.dump(cfg, f)

        sys.exit(0)



    # the following code is only for network funktionality or local usage
    # do ray casting for each transmitter (over network)
    nparts = len(cfg["calculationServers"]) + 1
    transmittermap = []

    for t in range(nparts):
        transmittermap.append([])

    transmitters = cfg["transmitters"]
    if len(cfg["transmitters"]) > cfg["numberWorkers"] and len(cfg["calculationServers"]) > 0:
        print("Do ray casting over network...")

        for i, t in enumerate(cfg["transmitters"]):
            transmittermap[i % nparts].append(t)

        transmitters = transmittermap[0]

        for i, s in enumerate(cfg["calculationServers"]):
            t = transmittermap[i + 1]
            gl.logger.info("Init connection to " + str(s))
            sock = networking.startLinkClient(s, False)

            gl.logger.info("send data")
            networking.send(marshal.dumps(cfg), sock)
            for fn in [buildingspolyfilename,streetspolyfilename ,terrainpolyfilename]:
                f = open(fn, "rb")
                data = f.read()
                f.close()
                networking.send(data, sock)
            networking.send(marshal.dumps(t), sock)

            if cfg["receiverType"] == 4:
                f = open(receiverfile, "rb")
                data = f.read()
                f.close()
                networking.send(data, sock)

            sock.close()


    # do own part of calculation
    transmitterfile = workfolder + 'transmitters.cfg'
    savePositions4Launcher(transmitters, transmitterfile)
    wrapLauncher.calculateTransmitterParallel(workfolder, cfg, len(transmitters))


    # receive generated data
    if len(cfg["transmitters"]) > cfg["numberWorkers"] and len(cfg["calculationServers"]) > 0:
        print("Receive Data...")
        for i, s in enumerate(cfg["calculationServers"]):
            sock = networking.startLinkClient(s, True, config["port"])
            net_identifier = networking.receive(sock)
            for t in transmittermap[i + 1]:
                x, y, z = t
                t = "[{0:g}, {1:g}, {2:g}]".format(x, y, z)
                f = open(coveragefolder + str(t) + '.txt', 'w')
                data = networking.receive(sock)
                f.write(data)
                f.close()
                if cfg["debugRays"] is True:
                    f = open(rayfolder + str(t) + '.txt', 'w')
                    data = networking.receive(sock)
                    f.write(data)
                    f.close()
            for string in [logEdge, logScript, logLauncher]:
                f = open(workfolder + fLogs + net_identifier + '_' + string, 'w')
                data = networking.receive(sock)
                f.write(data)
                f.close()
            # f = open(workfolder + fLogs + net_identifier + "_launcher.log", 'w')
            # data = networking.receive(sock)
            # f.write(data)
            # f.close()
            # sock.close()
            print("Data retreived for", net_identifier)




    # prepare for ns-3
    print("Preparing data for ns-3...")
    ns3filename = fOutputfiles + identifier + ".txt"
    prepare4ns3.prepare4ns3(coveragefolder, ns3filename, borders, cfg)

    if (cfg["debugLevel"]) >= 3:
        extractEdges.toBin(buildingsedgesfilename, buildingsedgesbinfilename)
        extractEdges.toBin(terrainedgesfilename, terrainedgesbinfilename)

    if cfg["debugRays"] is True:
        for transmitter in cfg["transmitters"]:
            x, y, z = transmitter
            string = "[{0:g}, {1:g}, {2:g}].txt".format(x, y, z)
            rayfilename = rayfolder + string
            raybinfilename = rayfilename[:-3] + "bin"
            gl.logger.debug("Make file: " + str(rayfilename) + "viewable")
            makeViewable.makeViewable(rayfilename, raybinfilename)

    # generate zip with results
    gl.logger.info("generating viewerconfig")
    saveViewerConfig(identifier, cfg)

    gl.logger.info("generating zipfile")
    saveAsZip(identifier, workfolder, cfg['debugLevel'], cfg["debugRays"])

    gl.logger.info("total time: " + str(time.time() - st))

    print("Finished.")


def parseCommand(cfg, cmd=None):
    """
    Parses program parameters
    :param cfg: current config dictionary
    :param cmd: program params as string
    :return: cfg: updated dictionary
    :return: mapParsed: True if inputmapfile-extension is zip
    """
    mapParsed = False

    # For clusterusage
    if cmd is not None:
        sys.argv[1:] = cmd.split(" ")

    # evaluate commandline
    params = len(sys.argv)

    if params < 2:
        print("Invalid amount of arguments!", USAGE)
        sys.exit()

    if sys.argv[1] == "-g":
        saveConfigFile(cfg, "sampleconfig.cfg")
        print("Created a sample configfile \"sampleconfig.cfg\" in the configfiles-directory.")
        sys.exit()

    if not os.path.isfile(sys.argv[1]) or sys.argv[1].split(".")[-1] not in ["gml", "osm", "raw", "zip"]:
        print("Invalid extension for mapfile!", USAGE)
        sys.exit()

    if sys.argv[-1] == "-m":
        cfg["name"] = "mapOnly"
        sys.argv = sys.argv[:-1]

    if sys.argv[1].split(".")[-1] == "zip":
        mapParsed = True

    # Parse params
    for j in range(2, len(sys.argv), 1):
        # reading inputfiles
        if os.path.isfile(sys.argv[j]) or os.path.isfile(fConfigfiles + sys.argv[j]):
            f = sys.argv[j]
            filetype = f.split(".")[-1]
            if filetype == "tr":
                cfg["transmitters"] = f
            elif filetype == "rec":
                cfg["receivers"] = f
            elif filetype == "cfg":
                config2 = parseConfigFile(f)
                cfg = mergeDict(cfg, config2)
            else:
                print("Skipping invalid filetype:", filetype)

        # reading params
        else:
            key = sys.argv[j].split("=")[0]
            value = sys.argv[j].split("=")[1]
            print("Processing key:", key)
            if key not in list(cfg.keys()):
                print("Skipping invalid parameter:", key)
            else:
                try:
                    cfg[key] = eval(value)
                except (KeyError, NameError, SyntaxError):
                    cfg[key] = value.strip()

    evaluateConfig(cfg)

    return cfg, mapParsed

def setConfig(cfg):
    """
    Sets config dictionary from commandline params
    :param cfg: current config dictionary
    """

    # get mapname and -type from filename
    inputmap = sys.argv[1]
    mapname = inputmap.split("/")[-1][:-4]
    cfg["mapName"] = mapname
    inputtype = inputmap.split(".")[-1]  # cardtype gml/osm

    if cfg["name"] == "auto":
        td = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d-%H%M%S')
        cfg["name"] = td

    # created identifier, workfolder in tmp/ and resultfiles will be named after it
    identifier = createIdentifier(cfg)
    print("Identifier:", identifier)

    # create directory tree for current simulation
    gl.mkdir(fTmp)
    workfolder = fTmp + identifier + '/'
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("fTmp: ", fTmp)
    print("Workfolder: ", workfolder)
    if cfg["preprop"]:
        gl.rmdir(workfolder)
    gl.mkdir(workfolder)
    gl.mkdir(workfolder + fPolygons)
    gl.mkdir(workfolder + fEdges)
    gl.mkdir(workfolder + fRays)
    gl.mkdir(workfolder + fLogs)
    gl.mkdir(fInputfiles)
    gl.mkdir(fConfigfiles)
    gl.mkdir(fOutputfiles)

    gl.initLogger(workfolder + fLogs, identifier, cfg["debugLevel"])

    # parse receiver or transmitter positions from file if given
    inputfile = str(cfg["transmitters"])
    if os.path.isfile(inputfile):
        saveInConfigfolder(inputfile, identifier)
        tp, tr = parsePositionsFile(inputfile)
        if tp == 1:
            tr = line2List(tr)
        cfg["transmitters"] = tr
        cfg["transmitterType"] = tp
    inputfile = str(cfg["receivers"])
    if os.path.isfile(inputfile):
        saveInConfigfolder(inputfile, identifier)
        tp, rec = parsePositionsFile(inputfile)
        cfg["receivers"] = rec
        cfg["receiverType"] = tp

    # specify transmitterType
    if cfg["transmitters"] == "area":
        cfg["transmitterType"] = 2
    elif cfg["transmitters"] == "cubic":
        cfg["transmitterType"] = 3
    elif cfg["transmitters"] == "street":
        cfg["transmitterType"] = 4
    else:
        if len(cfg["transmitters"]) > 1 and not isinstance(cfg["transmitters"][0], tuple):
            cfg["transmitterType"] = 4

    # specify receiverType
    if cfg["receivers"] == "full" or cfg["receivers"] == "auto":
        if cfg["coverageLevel"] < cfg["coverageMaxLevel"]:
            cfg["receiverType"] = 3
        else:
            cfg["receiverType"] = 2
    else:
        if len(cfg["receivers"]) > 1 and not isinstance(cfg["receivers"][0], tuple):
            cfg["receiverType"] = 4

    receiverfile = workfolder + "receivers.cfg"
    if cfg["receiverType"] in [1, 4]:
        savePositions4Launcher(cfg["receivers"], receiverfile)

    #print cfg["transmitters"], cfg["transmitterType"]
    #print cfg["receivers"], cfg["receiverType"]

    # set receiveThreshold
    if cfg["receiveThreshold"] == "full":
        ss = cfg["stepSize"]
        cfg["receiveThreshold"] = np.sqrt(3 * (ss ** 2)) / 2.
        gl.logger.info("ReceiveThreshoold set to: " + str(cfg["receiveThreshold"]) + "| Stepsize is " + str(ss))

    configfilename = identifier + ".cfg"
    saveConfigFile(cfg, configfilename)

    return workfolder, inputmap, inputtype, configfilename, receiverfile, identifier, cfg


def parseMap(workfolder, inputmap, inputtype, cfg, configfilename, mapOnly):
    """
    Extracts polygoncoordinates from mapfiles, removes the offset and stores the information in files
    :param workfolder: workfolder
    :param inputmap: inputmap filename
    :param inputtype: type of map
    :param cfg: config dictionary
    :param configfilename: configfilename
    :param mapOnly: program exits after extraction if True
    :return: uptaded config dictionary
    """
    st = time.time()

    buildingspolyfilename = workfolder + fPolygons + fileBuildings
    streetspolyfilename   = workfolder + fPolygons + fileStreets
    terrainpolyfilename   = workfolder + fPolygons + fileTerrain

    if cfg["preprop"]:
        # parse mapfile
        gl.logger.debug("Parsing mapfile: " + inputmap)
        rawpolyfilename = workfolder + fPolygons + "map_raw.txt"
        rawsteetfilename = workfolder + fPolygons + "street_raw.txt"
        if inputtype == "gml":
            gmlfilename = inputmap
            parseGML.parse(gmlfilename, rawpolyfilename)
        elif inputtype == "osm":
            osmfilename = inputmap
            parseOSM.parse(osmfilename, rawpolyfilename, rawsteetfilename, cfg)
        elif inputtype == "raw":
            gl.copy(inputmap, rawpolyfilename)
        else:
            raise Exception("invalid filetype: " + inputtype)
        gl.logger.debug("... parsed.")


        # remove offset
        gl.logger.debug("Removing offset")
        removeOffset.removeOffsetWithStreets(rawpolyfilename, rawsteetfilename, buildingspolyfilename, streetspolyfilename, cfg["center"])
        gl.logger.debug("... removed")

        gl.logger.debug("Write buildings in binary format")
        buildingspolybinfilename = workfolder + fPolygons + binBuildings
        parseToBinary.parse(buildingspolyfilename, buildingspolybinfilename)
        gl.logger.debug("... written")


        # calculate terrain
        gl.logger.debug("Calculating terrain")
        if inputtype in ["osm","raw"]:
            bordersfloat = calculateTerrain.calculate(buildingspolyfilename, terrainpolyfilename, cfg)
        else:
            bordersfloat = calculateTerrain.GML(buildingspolyfilename, terrainpolyfilename, cfg)
        gl.logger.debug("... calculated")

        gl.logger.debug("Write terrain in binary format")
        terrainpolybinfilename = workfolder + fPolygons + binTerrain
        parseToBinary.parse(terrainpolyfilename, terrainpolybinfilename)
        gl.logger.debug("... written")

        borders = []
        for b in bordersfloat:
            borders.append(int(b))

        if not cfg["borders"]:
            cfg["borders"] = borders
            saveConfigFile(cfg, configfilename)
        else:
            borders = cfg["borders"]

    else:
        borders = cfg["borders"]

    gl.logger.info("Borders: " + str(borders))
    runtime = time.time() - st
    gl.logger.info("Total Time for Map Preparation: " + str(runtime))

    # c++ launcher does edge-extraction now

    if mapOnly:

        # Our patch zipfile_.py is not working in 2.6.x and might not work in versions lower 2.7.9
        import sys
        if sys.version_info[0] == 2 and sys.version_info[1] == 7 and sys.version_info[2] < 9:
            from .src.util import zipfile_ as zipfile
        else:
            import zipfile

        zipfname = fInputfiles + cfg["mapName"] + ".zip"

        zipf = zipfile.ZipFile(zipfname, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)
        zipf.write(buildingspolyfilename, fileBuildings)
        zipf.write(streetspolyfilename, fileStreets)
        zipf.write(terrainpolyfilename, fileTerrain)

        bordersfile = workfolder + fPolygons + 'borders.txt'
        with open(bordersfile, 'w') as bf:
            np.savetxt(bf, [borders])
        zipf.write(bordersfile, 'borders.txt')
        zipf.close()
        gl.logger.info("Zipfile created. Exiting ...")
        sys.exit(0)

    return cfg


def copyInputFiles(zipf, workfolder, cfg, configfilename):
    """
    Extract prepared mapfiles from the input zipfile into the right location in the workfolder
    :param zipf: inputzipfile
    :param workfolder: workfolder
    :param cfg: config dictionary
    :param configfilename: configfilename
    :return: updated config dictionary
    """

    zf = zipfile.ZipFile(zipf, 'r')

    for file in zf.namelist():
        zf.extract(file, workfolder + fPolygons)

    # parse borders into the config dictionary
    cfg["borders"] = np.genfromtxt(workfolder + fPolygons + "borders.txt", delimiter=" ")
    saveConfigFile(cfg, configfilename)
    return cfg


def spawnJobs(cfg, workfolder):
    """
    Create Job Spawnscripts, located in the workfolder, which will be submitted to start calculation
    :param cfg: config dictionary
    :param workfolder: workfolder
    """

    if cfg["clusterType"] == 0: # inf-cluster
        clusterCommand = createTorqueCommand
    else:
        clusterCommand = createPBSProCommand

    import subprocess
    # solution found on https://stackoverflow.com/questions/4814970/subprocess-check-output-doesnt-seem-to-exist-python-2-6-5
    if "check_output" not in dir( subprocess ): # duck punch it in!
        def f(*popenargs, **kwargs):
            if 'stdout' in kwargs:
                raise ValueError('stdout argument not allowed, it will be overridden.')
            process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
            output, unused_err = process.communicate()
            retcode = process.poll()
            if retcode:
                cmd = kwargs.get("args")
                if cmd is None:
                    cmd = popenargs[0]
                raise subprocess.CalledProcessError(retcode, cmd)
            return output
        subprocess.check_output = f

    # cut unnecessary information from the typeString, information for type 1/4 is written to files in the workfolder
    typeString = wrapLauncher.createTypeString(cfg)
    typeString = str(typeString if int(typeString[0]) not in [1,4] else typeString[0])


    try:
        # spawn edge extraction
        cmd = cppFiles + cppEdge + ' ' + workfolder
        cluster_header = clusterCommand(cfg, name=clusterEdgeName, msg=clusterEdgeMsg, mem=clusterEdgeMem)
        gl.logger.debug("\n" + str(cluster_header) + str(cmd))

        qsubfile = workfolder + clusterEdgeName + '.sh'
        with open(qsubfile, 'w') as cmdfile:
            cmdfile.write(cluster_header)
            cmdfile.write(cmd)

        qsub = 'qsub ' + qsubfile
        gl.logger.debug(str(qsub))
        output = subprocess.check_output(qsub, shell=True)
        gl.logger.info("Qsub-output: " + str(output))


        # spawn launcher
        typeString = "'" + typeString + "'"
        launcher = [cppFiles + cppLauncher,
                    workfolder,
                    typeString,
                    '$PBS_ARRAY_INDEX' if cfg["clusterType"] == 1 else '$PBS_ARRAYID',
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
                    str(cfg["timeout"])]

        cmd = ' '.join(launcher)
        if len(cfg["transmitters"]) == 1:
            cluster_header = clusterCommand(cfg, name=clusterLauncherName, mem=clusterLauncherMem, msg=clusterLauncherMsg)
            launcher[3] = str(0)
        else:
            cluster_header = clusterCommand(cfg, name=clusterLauncherName, mem=clusterLauncherMem, msg=clusterLauncherMsg, array='0-'+str(len(cfg["transmitters"]) - 1))

        gl.logger.debug("\n" + str(cluster_header) + str(cmd))

        qsubfile = workfolder + clusterLauncherName + '.sh'
        with open(qsubfile, 'w') as cmdfile:
            cmdfile.write(cluster_header)
            cmdfile.write(cmd)

        qsub = 'qsub -W depend=afterok:' + output[:-1] + ' ' + qsubfile
        gl.logger.debug(str(qsub))
        output = subprocess.check_output(qsub, shell=True)
        gl.logger.info("Qsub-output: " + str(output))


        #spawn collect
        cmd = 'python collectData.py ' + workfolder + createIdentifier(cfg) + '.dump'

        cluster_header = clusterCommand(cfg, clusterCollectName, msg=clusterCollectMsg, mem=clusterCollectMem)
        gl.logger.debug("\n" + str(cluster_header) + str(cmd))

        qsubfile = workfolder + clusterCollectName + '.sh'
        with open(qsubfile, 'w') as cmdfile:
            cmdfile.write(cluster_header)
            cmdfile.write(cmd)

        depend = 'afterok:' if cfg["clusterType"] == 1 else 'afterokarray:'
        qsub = 'qsub -W depend=' + depend + output[:-1] + ' ' + qsubfile
        gl.logger.debug(str(qsub))
        output = subprocess.check_output(qsub, shell=True)
        gl.logger.info("Qsub-output: " + str(output))

    except subprocess.CalledProcessError as e:
        gl.logger.info(str(e))


if __name__ == "__main__":

    main()
