from port3_ralans.viewer2d import *

def ralans_packet_received(node_index=1, filename="", height=1, 
        stepsize=5, isZip=True):
    """calculates whether the given node can connect to another cell on the map. It
    calculates the signal strength to every cell in the grid.

    :node_index: the index of the node
    :filename: the path to the RaLaNS file. It has to be a zip file.
    :returns: true, if there is a connection from node 1 to node 2.
            false, else.
    """

    # TODO open file at correct position, so that it is just done ones

    bdfile = None
    if isZip:
        resfile, bdfile, configfile = getFiles(filename)
        config = parseConfigFile(configfile, isZip=isZip)

    # TODO change encoding of pint in grid
    requestedTransmitter = [0,0]
    requestedTransmitter.append(height)
    res, borders, transmitter, stp = parseResFile.parseResFile(filename, 
            requestedTransmitter, stepsize)
    print(res.shape)
    np.place(res, np.logical_not(np.isfinite(res)), -1000)
    for i in res:
        print(i)

    limits = [borders[0], borders[2], borders[1], borders[3]]
    print(limits)

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
    plt.show()

ralans_packet_received(filename="/home/joris/workspace/RaLaNS_data/small_street_flat_cover/result.txt", 
        isZip=False)
