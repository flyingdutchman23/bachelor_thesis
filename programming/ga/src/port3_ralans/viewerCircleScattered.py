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
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Circle
import time
import sys
import os
import zipfile
from . import src.util.parseResFile as pf
from .src.util import drawBuildings
from .src.util.functions import parseConfigFile
from .src.config import fPolygons, fileBuildings


def getFiles(zipf):

    zf = zipfile.ZipFile(zipf, 'r')

    rf = 'result.txt'
    cf = 'config.cfg'
    resfile = zf.open(rf)
    configfile = zf.open(cf)

    bf = fPolygons + fileBuildings
    bdfile = None
    try:
        bdfile = zf.open(bf)
    except:
        print("No polygon-file found! Will not draw a map.")

    rechead = 0
    for i, l in enumerate(resfile):
        if i == 1:
            rechead = int(l[0])
            break
    resfile.close()
    resfile = zf.open(rf)

    zf.close()

    print(rechead)
    if rechead != 4:
        print("This viewer is only for simulationtype 'list' or 'street'.")
        sys.exit()

    return resfile, bdfile, configfile


def plot(filename, reqTr, buildings=True):
    filename, bdfile, configfile = getFiles(filename)
    config = parseConfigFile(configfile, isZip=True)
    streng, borders, _, co = pf.parseResFile(filename, reqTr, config["stepSize"], None, isZip=True)
    filename.close()

    streng = np.array(streng[0])
    index = np.where(streng != np.inf)

    limits = [borders[0], borders[2], borders[1], borders[3]]

    fig, ax = plt.subplots()
    ax.axis(limits)
    ax.set_aspect(aspect='equal', adjustable='box')
    cmap = plt.cm.get_cmap("gnuplot2")

    print("generate circles")
    st = time.time()

    circles = []
    x = co[::3]
    y = co[1::3]
    r = config['receiveThreshold']
    for xy in zip(x, y):
        circles.append(Circle(xy=xy, radius=r))

    c = PatchCollection(np.array(circles)[index])
    c.set_cmap(cmap)
    c.set_alpha(0.6)
    c.set_clim([-100, 0])
    c.set_array(streng[index])
    ax.add_collection(c)
    print("Needed time: ", (time.time() - st))

    cb = plt.colorbar(c)

    if bdfile is not None and buildings:
        drawBuildings.draw(plt, (0,0,0), bdfile)

    cb.ax.tick_params(labelsize=18)
    cb.set_label("signal strength [dB]", fontsize=20)
    plt.tight_layout(1.0)

    return plt


def main(command=None):
    # For clusterusage
    if command is not None:
        sys.argv[1:] = command.split(" ")

    usage = "Usage: python viewerScattered.py <input.zip> [<transmitter>] [-b | 3d]"

    params = len(sys.argv)

    b = False
    if sys.argv[-1] == '-b':
        b = True
        params -= 1

    reqTr = None

    # print params, sys.argv[-1][-3:], os.path.isfile(sys.argv[1])

    if params < 2 or sys.argv[1][-3:] != 'zip' or not os.path.isfile(sys.argv[1]):
        print("No zipfile specified! " + usage)

    if params == 3:
        try:
            reqTr = eval(sys.argv[2])
        except:
            print("Invalid transmitter:", sys.argv[2])

    plt = plot(sys.argv[1], reqTr, b)

    plt.show()


if __name__ == "__main__":
    main()
"""
import matplotlib.pyplot as plt
from matplotlib.patches import Circle # for simplified usage, import this patch

# set up some x,y coordinates and radii
x = [1.0, 2.0, 4.0]
y = [1.0, 2.0, 2.0]
r = [1/(2.0**0.5), 1/(2.0**0.5), 0.25]

fig = plt.figure()

# initialize axis, important: set the aspect ratio to equal
ax = fig.add_subplot(111, aspect='equal')

# define axis limits for all patches to show
ax.axis([min(x)-1., max(x)+1., min(y)-1., max(y)+1.])

# loop through all triplets of x-,y-coordinates and radius and
# plot a circle for each:
for x, y, r in zip(x, y, r):
    ax.add_artist(Circle(xy=(x, y),
                  radius=r))

plt.show()
"""
