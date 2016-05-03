#to plot
import matplotlib.pyplot as plt

###helper module to plot specific states and results

def avg_min_max(logbook):
    gen = logbook.select("gen")
    fit_mins = logbook.select("min")
    fit_maxs = logbook.select("max")
    fit_avgs = logbook.select("avg")

    fig, ax1 = plt.subplots()
    print("gen",gen)
    print("fit_mins",fit_mins)
    line1 = ax1.plot(gen, fit_mins, "b", label="Minimum Fitness")
    line2 = ax1.plot(gen, fit_maxs, "g", label="Maximum Fitness")
    line3 = ax1.plot(gen, fit_avgs, "r", label="Average Fitness")
    ax1.set_xlabel("Generation")
    ax1.set_ylabel("Fitness")
    # for tl in ax1.get_yticklabels():
        # tl.set_color("b")

    lns = line1 + line2 + line3
    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc="center right")

    plt.show()

def map(data,name):

    values = np.reshape(data,(ROWS,COLS))
    plt.imshow(values, vmin=0, vmax=max(data), interpolation="nearest",
            cmap=plt.get_cmap("gnuplot2"), origin="lower")
    cb = plt.colorbar()
    plt.ylabel("y [m]")
    plt.xlabel("x [m]")
    cb.set_label(name)
    #TODO save plot
    #plt.savefig(savename)

    #show the plot
    plt.show()

def nodes_radius(data,individual,name):

    #to have an array with just 0 and 1
    for i, d in enumerate(data):
        if d != 0:
            data[i] = 1
    data = np.add(data,individual)
    map_plot(data,name)
    return None
