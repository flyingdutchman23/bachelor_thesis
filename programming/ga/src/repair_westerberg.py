import sys
import io
import numpy as np
import constants

import my_util

import ralans_helper

def repair():
    """TODO: Docstring for repair.

    :arg1: TODO
    :returns: TODO

    """
    folder = "/home/joris/workspace/RaLaNS_data/westerberg_full/"
    filename = "westerberg_full_try.txt"
    filepath = folder + filename
    newfilename = "westerberg_full_new.txt"
    newfilepath = folder + newfilename
    i = 1
    with open(filepath, "r") as input:
        with open(newfilepath,"wt") as output: 
            for l in input:
                line = ralans_helper.conv_byte_to_str(l)
                try:
                    linelist = np.loadtxt(io.StringIO(line)
                            , delimiter=" ").tolist()
                except Exception as e:
                    print("error in line: ", i)
                    print(l)
                    print(e)
                    sys.exit()
                if len(linelist) < 3:
                    sys.exit("Fault!")
                elif len(linelist) > 3:
                    output.write(l)
                i += 1


if __name__ == "__main__":
    repair()
                

