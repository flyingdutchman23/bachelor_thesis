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
import numpy as np
import sys
import zipfile

import matplotlib.pyplot as plt

from .src.util import parseResFile
from .src.config import fOutputfiles


def getFiles(zipf):

    zf = zipfile.ZipFile(zipf, 'r')

    rf = 'result.txt'
    resfile = zf.open(rf)

    rechead = 0
    for i, l in enumerate(resfile):
        if i == 1:
            rechead = int(l[0])
            break
    resfile.close()
    resfile = zf.open(rf)

    zf.close()

    if rechead not in [1, 2, 3]:
        print("Lists and Points are not supported.")
        sys.exit()

    return resfile


def getSignalFromTo(resfile, pointf, pointt, transmitter, layer=None):
    res, borders, transmitter, stp = parseResFile.parseResFile(resfile, transmitter, requestedLayer=layer, isZip=True)

    signals = []
    if pointf is not None:
        transmitter[0] = pointf[0]
        transmitter[1] = pointf[1]
        transmitter[2] = pointf[2]

    x0 = transmitter[0]
    y0 = transmitter[1]
    z = transmitter[2]
    x1 = pointt[0]
    y1 = pointt[1]
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    # print borders[2]
    # print transmitter[0]
    # print pointt[0]


    sx = stp[0] if x0 <= x1 else -stp[0]
    sy = stp[1] if y0 <= y1 else -stp[1]
    # print borders, dx, dy, "|", sx, sy, "|", x0, y0, "|", x1, y1
    err = dx + dy

    while True:
        # print x0, x1, sx, " --|--, print y0, y1, sy
        signals.append(getLink((x0, y0, z), res, borders, stp))
        if ((x0 >= x1 and y0 >= y1 and sx > 0 and sy > 0) or
                (x0 <= x1 and y0 <= y1 and sx < 0 and sy < 0) or
                (x0 >= x1 and y0 <= y1 and sx > 0 and sy < 0) or
                (x0 <= x1 and y0 >= y1 and sx < 0 and sy > 0)):
            break
        e2 = 2 * err
        if e2 > dy:
            err += dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

    signals = np.array(signals)

    # print "Signals", signals

    return signals, borders, transmitter, stp


def getLink(receiver, res, borders, stp):
    dx = abs(borders[0] / stp[0])
    dy = abs(borders[1] / stp[1])

    rx = int(receiver[0] / stp[0] + dx)
    ry = int(receiver[1] / stp[1] + dy)

    value = -3000.0
    try:
        # print res[ry]
        # print "pick", ry, rx, res[ry][rx]
        value = res[ry][rx]
    except:
        if True:
            print("unable to pick :", rx, ry)
    return value


def plotLine(patterncnt, filename, transmitter, layer=None):

    pattern = ["-", "--", "-.", "."]

    resfile = getFiles(filename)

    res, borders, transmitter, stp = parseResFile.parseResFile(resfile, transmitter, requestedLayer=layer, isZip=True)

    veca = [borders[0], borders[1], 1.]
    vecb = [borders[2], borders[3], 1.]

    rng = []
    cnt = 0
    for i in parseResFile.frange(0, len(res[0]) -1, 1):
        cnt += 1
        rng.append(i)
    # print "len res", len(res[0]), "len range", cnt

    plt.plot(rng,
             res[0], pattern[patterncnt % len(pattern)], label=str(veca[0:2]) + " to " + str(vecb[0:2]), linewidth=2)

    return plt


def plot(patterncnt, filename, pointf, pointt, transmitter, layer=None):
    pattern = ["-", "--", "-.", "."]

    resfile = getFiles(filename)

    signals, borders, transmitter, stp = getSignalFromTo(resfile, pointf, pointt, transmitter, layer)

    dx = pointt[0] - transmitter[0]
    dy = pointt[1] - transmitter[1]
    # print borders, dx, dy

    leng = np.sqrt(dx ** 2 + dy ** 2)
    if pointt[0] == 0:
        stepsize = stp[0]
    elif pointt[1] == 0:
        stepsize = stp[1]
    else:
        if not len(signals) == 1:
            stepsize = leng / (len(signals) - 1)
        else:
            stepsize = leng
    range = np.arange(0., len(signals) * stepsize - stepsize / 2, stepsize)


    # print "#########################################################"
    # print np.arange(transmitter[0], pointt[0] - transmitter[0], stp[0])
    # print np.arange(borders[1], stp[1] * len(signals) + borders[1], stp[1])
    # print "length:  ", leng
    # print "stepsize:", stepsize
    # print "len(sig):", len(signals)
    # print "signals: ", signals
    # print "len(rng):", len(range)
    # print "range:  ", range
    # print pattern[patterncnt % len(pattern)]
    # print "#########################################################"

    plt.plot(range,
             signals, pattern[patterncnt % len(pattern)], label=str(transmitter) + " to " + str(pointt), linewidth=2)
    """
    patterncnt += 1

    plt.legend(prop={'size': 10})
    plt.xlabel("x [m]")
    plt.ylabel(u"Signalstärke [dB]")
    plt.title(filename + " - signal strength trend")
    plt.show()
    """


def plotParams(argv):
    i = 1
    params = len(argv)
    patterncnt = 0

    while True:
        # print params, i, patterncnt
        layer = None
        filename = argv[i]
        transmitter = None
        i += 1

        if argv[i] == "-t":
            if i + 1 < params:
                try:
                    transmitter = eval(argv[i + 1])
                except:
                    print("Can't evaluate >" + str(argv[i + 1]) + "<. Using default transmitter.")
                i += 2
            else:
                print("Not enough params")

        if argv[i] == "l":
            i += 1
            plotLine(patterncnt, filename, transmitter)
        else:

            receiver = argv[i]
            i += 1

            try:
                pt = eval(receiver)
                # i += 1
                pf = None
            except:
                p = receiver.split("to")
                # print p
                pt = eval(p[1])
                pf = eval(p[0])

            if i < params:
                #print argv[i], i, "layer", int(argv[i])
                try:
                    layer = int(argv[i])
                    i += 1
                    print("Use layer:", layer)
                except:
                    print("Can't evaluate layer > ", argv[i], " <. Using first layer.")

            # print filename, transmitter, layer, pf, pt

            plot(patterncnt, filename, pf, pt, transmitter, layer)

        if i + 2 > params:
            break

        patterncnt += 1

    plt.legend(prop={'size': 10})
    plt.xlabel("x [m]")
    plt.ylabel("signal strength [dB]")

    return plt


def main(command=None):
    # For clusterusage
    if command is not None:
        sys.argv[1:] = command.split(" ")

    usage = "python <input.zip> [t <transmitter>] <receiver>[to<reciever>] [<input.zip> [t <transmitter>] <receiver>[to<reciever>] ...] [s <name>]\n" \
            "For receivertype 'line' use: python <input.zip> l [t <transmitter>] s <name>]"
    if len(sys.argv) < 3:
        print(usage)
    else:
        if sys.argv[-2] == "-s":
            plt = plotParams(sys.argv[:-2])
            name = sys.argv[-1]
            plt.savefig(name + ".png", bbox_inches='tight')
            plt.savefig(name + ".pdf", bbox_inches='tight')
        else:
            plt = plotParams(sys.argv)
            plt.show()


if __name__ == "__main__":
    main()
