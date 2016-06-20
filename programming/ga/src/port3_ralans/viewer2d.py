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
import zipfile
import numpy as np
from io import StringIO

import matplotlib.pyplot as plt

from .src.util import parseResFile
from .src.util.functions import parseConfigFile
from .src.config import fPolygons, fileBuildings
from .src.util import drawBuildings


def getFiles(zipf):

    zf = zipfile.ZipFile(zipf, 'r')

    rf = 'result.txt'
    cf = 'config.cfg'
    bf = fPolygons + fileBuildings

    resfile = zf.open(rf)
    configfile = zf.open(cf)
    bdfile = None
    try:
        bdfile = zf.open(bf)
    except:
        print("No polygon-file found! Will not draw a map.")

    rechead = 0
    # for i, l in enumerate(resfile):
        # print("index: ",i," content: ", l)
        # if i == 1:
            # rechead = int(chr(l[0]))
            # break
    # resfile.close()
    # resfile = zf.open(rf)

    zf.close()

    # print("rechead",rechead)
    # if rechead == 1:
        # print("Lines are not supported yet.\n Use 1d-Viewer to display the signal strength trend.")
    # if rechead == 4:
        # print("Please use viewerScattered.py for 'lists'.")
    # if rechead not in [2, 3]:
        # print("Only 'area' and 'cubic' are supported simulationtypes for this viewer.")
        # sys.exit()

    return resfile, bdfile, configfile


def plot(zipf, requestedTransmitter=None, requestedLayer=None):
    resfile, bdfile, configfile = getFiles(zipf)

    config = parseConfigFile(configfile, isZip=True)

    res, borders, transmitter, stp = parseResFile.parseResFile(resfile, requestedTransmitter, config["stepSize"],
                                                               requestedLayer, isZip=True)
    resfile.close()

    # alternative fix for pdf saving bug (other fix didn't work after editing the pdf and printing it)
    np.place(res, np.logical_not(np.isfinite(res)), -1000)

    limits = [borders[0], borders[2], borders[1], borders[3]]

    fig, ax = plt.subplots()
    ax.set_aspect(aspect='equal', adjustable='box')
    cmap = plt.get_cmap("gnuplot2")

    im = plt.imshow(res, vmin=-100, vmax=0, interpolation="nearest", cmap=cmap, origin="lower")
    im.set_extent(limits)
    cb = plt.colorbar()
    cb.ax.tick_params(labelsize=18)
    cb.set_label("signal strength [dB]", fontsize=20)

    if bdfile is not None:
        color = 'w'
        color = (1,1,1)
        drawBuildings.draw(plt, color, bdfile)


    plt.ylabel("y [m]", fontsize=20)
    plt.xlabel("x [m]", fontsize=20)
    plt.xticks(fontsize=17)
    plt.yticks(fontsize=17)

    plt.tight_layout(1.0)
    return plt


def diff(zipf1, reqTr1, reqL1, zipf2, reqTr2, reqL2):
    resfile1, bdfile1, configfile1 = getFiles(zipf1)
    resfile2, bdfile2, configfile2 = getFiles(zipf2)
    if bdfile2 is not None: bdfile2.close()

    config1 = parseConfigFile(configfile1, isZip=True)
    config2 = parseConfigFile(configfile2, isZip=True)

    # print "parseResFile, transmitter: ", reqtr1

    res1, borders1, transmitter1, stp = parseResFile.parseResFile(resfile1, reqTr1, config1["stepSize"], reqL1, isZip=True)
    resfile1.close()
    res2, borders2, transmitter2, stp2 = parseResFile.parseResFile(resfile2, reqTr2, config2["stepSize"], reqL2, isZip=True)
    resfile2.close()

    # TODO
    # ASSERT stepsize is identical maybe? res is the same?
    # assert borders1[2] == borders2[2] and borders1[3] == borders2[3]
    # newborders = np.max([borders1, borders2], axis=0)

    c = plt.get_cmap("RdBu")
    c.set_bad('k')
    plt.figure()
    im = plt.imshow(res2 - res1, vmin=-20, vmax=20, interpolation="none", cmap=c, origin="lower")

    limits = [borders1[0], borders1[2], borders1[1], borders1[3]]
    im.set_extent(limits)
    # im.set_extent([newborders[1], maxy, maxx, newborders[0]])
    plt.ylabel("y [m]", fontsize=20)
    plt.xlabel("x [m]", fontsize=20)

    cb = plt.colorbar()
    cb.ax.tick_params(labelsize=18)
    cb.set_label("signal strength difference [dB]", fontsize=20)

    """
    print borders1
    print borders2
    print newborders
    print len(res1), len(res1[0])
    print len(res2), len(res2[0])
    print "findmax"
    """
    # maxxs = [len(res1) * newborders[2] + borders1[0], len(res2) * newborders[2] + borders2[0]]
    # maxys = [len(res1[0]) * newborders[3] + borders1[1], len(res2[0]) * newborders[3] + borders2[1]]
    # print maxxs
    # print maxys
    # maxx = np.min(maxxs)
    # maxy = np.min(maxys)
    # xlen = int((maxx - newborders[0]) / newborders[2])
    # ylen = int((maxy - newborders[1]) / newborders[3])
    # print maxx, maxy

    # print "ints"
    # print xlen, ylen

    # xlim = int((newborders[0] - borders2[0]) / newborders[2])
    # ylim = int((newborders[1] - borders2[1]) / newborders[3])
    # print xlim, xlen, len(res2)
    # print ylim, ylen, len(res2[0])
    # res2 = res2[xlim:xlim + xlen, ylim:ylim + ylen]

    # xlim = int((newborders[0] - borders1[0]) / newborders[2])
    # ylim = int((newborders[1] - borders1[1]) / newborders[3])
    # print xlim, xlen, len(res1)
    # print ylim, ylen, len(res1[0])
    # res = res1[xlim:xlim + xlen, ylim:ylim + ylen]


    if bdfile1 is not None:
        color = 'w'
        color = (0.5019607843137255, 0.5019607843137255, 0.5019607843137255)
        drawBuildings.draw(plt, color, bdfile1)

    plt.xlim([limits[0], limits[1]])
    plt.ylim([limits[2], limits[3]])
    plt.xticks(fontsize=17)
    plt.yticks(fontsize=17)

    plt.tight_layout(1.0)
    return plt


def invalidFiletype(filename, usage=""):
    if filename.split('.')[-1] != 'zip':
        print("Invalid inputfiletype, required zipfile! \n" + usage)
        sys.exit()


def validPosition(pos):
    reqTr = None
    try:
        reqTr = eval(pos)
    except:
        print("Invalid transmitter:", pos)
    return reqTr


def validLayer(l):
    reqL = None
    try:
        reqL = float(l)
    except:
        print("Invalid layer:", l)
    return reqL


def parseOptions(opt):
    leng = len(opt)
    res = None

    if leng == 0:
        return None, None

    elif leng == 1:
        try:
            res = eval(opt[0])
        except:
            print("Invalid option:", opt[0])

        if isinstance(res, list):
            return res, None
        else:
            return None, res

    else:
        res1 = validPosition(opt[0])
        res2 = validLayer(opt[1])

        return res1, res2


def isdiff(params):
    ret = 0
    for i in range(2, len(params)):
        if params[i][-3:] == 'zip':
            ret = i
        i += 1
    return ret


def main(command=None):
    # For clusterusage
    if command is not None:
        sys.argv[1:] = command.split(" ")

    usage = "Usage: python viewer2d.py <input.zip> [transmitter] [layer] [<input2.zip [transmitter] [layer]] [-s <name>]" \
            "\n Layers are only available if the simulation type for receivers is 'cubic'."

    name = file2 = reqTr1 = reqTr2 = None
    reqL1 = reqL2 = None

    params = len(sys.argv)

    if params < 2:
        print("No zipfile specified! " + usage)
        sys.exit()
    if sys.argv[-2] == "-s":
        name = sys.argv[-1]
        params -= 2

    invalidFiletype(sys.argv[1], usage)
    file1 = sys.argv[1]

    if params > 2:
        secondInput = isdiff(sys.argv)
        if secondInput == 0:
            reqTr1, reqL1 = parseOptions(sys.argv[2:])
        else:
            reqTr1, reqL1 = parseOptions(sys.argv[2:secondInput])
            file2 = sys.argv[secondInput]
            if 1 < params - secondInput:
                reqTr2, reqL2 = parseOptions(sys.argv[secondInput + 1:])

    # print reqTr1, reqL1, reqTr2, reqL2


    print("Parsing data, this might take a few seconds for large maps")

    if file2 is None:
        # print file1, reqTr1
        plt = plot(file1, reqTr1, reqL1)
    else:
        plt = diff(file1, reqTr1, reqL1, file2, reqTr2, reqL2)

    if name is None:
        plt.show()
    else:
        plt.savefig(name + ".png", bbox_inches='tight')
        plt.savefig(name + ".pdf", bbox_inches='tight')


if __name__ == "__main__":
    main()
