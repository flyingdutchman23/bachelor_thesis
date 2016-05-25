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
from . import src.util.parseResFile as pf
import sys
import os
import zipfile
from io import StringIO
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


def plot3d(filename, reqTr):
    filename, bdfile, configfile = getFiles(filename)
    config = parseConfigFile(configfile, isZip=True)
    co, streng = pf.parseResFile(filename, reqTr, config["stepSize"], None, isZip=True)
    filename.close()
    x = []
    y = []
    z = []
    for i in range(0, len(co) / 3):
        x.append(co[i])
        y.append(co[i + 1])
        z.append(co[i + 1])
    area = 80

    im = plt.figure()
    ax = im.add_subplot(111, projection='3d')

    # plt.ylabel("y [m]", fontsize=20)
    # plt.xlabel("x [m]", fontsize=20)
    # plt.zlabel("z [m]", fontsize=20)

    cmap = plt.get_cmap("gnuplot2")
    s = ax.scatter(x, y, z, s=area, vmin=-100, vmax=0, cmap=cmap, c=streng)

    cb = im.colorbar(s)
    cb.ax.tick_params(labelsize=18)
    cb.set_label("signal strength [dB]", fontsize=20)
    return plt


def plot(filename, reqTr, buildings=True):
    filename, bdfile, configfile = getFiles(filename)
    config = parseConfigFile(configfile, isZip=True)
    streng, borders, _, co = pf.parseResFile(filename, reqTr, config["stepSize"], None, isZip=True)
    filename.close()
    x = []
    y = []

    for i in range(0, len(co) / 3):
        x.append(co[i * 3])
        # print co[i]
        y.append(co[i * 3 + 1])
    area = 80

    plt.ylabel("y [m]", fontsize=20)
    plt.xlabel("x [m]", fontsize=20)

    # print x
    # print y

    cmap = plt.cm.get_cmap("gnuplot2")

    import time
    st = time.time()
    plt.scatter(x, y, s=area, vmin=-100, vmax=0, cmap=cmap, c=streng, edgecolor="none")

    if bdfile is not None and buildings:
        print("Draw buildings...")
        for l in bdfile:
            poly = np.genfromtxt(StringIO(l), delimiter=" ")
            xs = poly[::3]
            ys = poly[1::3]
            # plt.fill(ys, xs, edgecolor="w", fill=False, hatch="\\\\\\\\")
            plt.fill(xs, ys, edgecolor="b", fill=False, hatch="\\\\\\\\")

        bdfile.close()

    limits = [borders[0], borders[2], borders[1], borders[3]]
    plt.xlim([limits[0], limits[1]])
    plt.ylim([limits[2], limits[3]])
    plt.gca().set_aspect('equal', adjustable='box')
    plt.draw()

    print("Needed time:", time.time() - st)
    cb = plt.colorbar()
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

    p3d = False
    b = False
    if sys.argv[-1] == '3d':
        p3d = True
        params -= 1
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

    if not p3d:
        plt = plot(sys.argv[1], reqTr, b)
    else:
        plt = plot3d(sys.argv[1], reqTr)

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

"""import matplotlib
from matplotlib.patches import Circle, Wedge, Polygon
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt


fig, ax = plt.subplots()

resolution = 50 # the number of vertices
N = 3
x       = np.random.rand(N)
y       = np.random.rand(N)
radii   = 0.1*np.random.rand(N)
patches = []
for x1,y1,r in zip(x, y, radii):
    circle = Circle((x1,y1), r)
    patches.append(circle)

x       = np.random.rand(N)
y       = np.random.rand(N)
radii   = 0.1*np.random.rand(N)
theta1  = 360.0*np.random.rand(N)
theta2  = 360.0*np.random.rand(N)
for x1,y1,r,t1,t2 in zip(x, y, radii, theta1, theta2):
    wedge = Wedge((x1,y1), r, t1, t2)
    patches.append(wedge)

# Some limiting conditions on Wedge
patches += [
    Wedge((.3,.7), .1, 0, 360),             # Full circle
    Wedge((.7,.8), .2, 0, 360, width=0.05), # Full ring
    Wedge((.8,.3), .2, 0, 45),              # Full sector
    Wedge((.8,.3), .2, 45, 90, width=0.10), # Ring sector
]

for i in range(N):
    polygon = Polygon(np.random.rand(N,2), True)
    patches.append(polygon)

colors = 100*np.random.rand(len(patches))
p = PatchCollection(patches, cmap=matplotlib.cm.jet, alpha=0.4)
p.set_array(np.array(colors))
ax.add_collection(p)
plt.colorbar(p)

plt.show()
"""
