RaLaNS MANUAL

This folder contains a software, that prepares a file with signal strengths for usage in ns-3.
FILES:
run.py : This is the main software, specify a mapfile as first param or -g to generate a sample configuration file.
         Set -m as second param to generate a zipfile with prepared mapdata for instant usage.
         All values in the sample configuration file are set by default. If you don't need other values, you don't have
         to specify a configuration file as command parameter.
         The weighting of the configuration values is the following:
         At first all default values will be restored.
         After that the script overwrites the default values with the values from the configuration file.
         The last step overwrites the current values with the values from the command line.
         
    optional parameters:
    configurationfile   : File extension has to be 'cfg', replaces default configuration with your configuration.
    transmitterfile     : File extension has to be 'tr', you can specify several transmitter positions.
    receiverfile        : File extension has to be 'rec', you can specify several receiver positions.
    <key>=<value>       : Accepts every key in the configfile as commandline argument and replaces current configuration
                          with the value given, make sure that you don't use spaces in one argument. A list with names and
                          descriptions of these parameters is given in /src/config.py.
    Usage: python run.py -g | mapfile [configfile] [transmitterfile] [receiverfile] [key=value]* | mapfile -m

viewer1d.py : Visualizes a signal strength trend between to points, specify the zipfile of your calculation and a point.
    optional parameters:
    t <transmitter>     : Loads coveragemap of specified transmitter.
    <point>to<point>    : Displays the signal strength along a line between these specific points.
    s <name>            : Saves plot as <name>.png and <name>.pdf, has to be the last param.

    If you want to display several signal trends in one plot, specify another (or the same) result zipfile and a point
    Usage: python <input.zip> [t <transmitter>] <receiver>[to<reciever>] [<input.zip> [t <transmitter>] <receiver>[to<reciever>] ...] [s <name>]
           python <input.zip> l [t <transmitter>] s <name>] (if your receiver-type is a line)

viewer2d.py : Visualizes a signal strength map, specify a result zipfile as first parameter.
    optional parameters:
    <transmitter>       : Loads coveragemap of specified transmitter.
    <layer>             : Loads coveragemap of specified layer (only available if receiver simulation type is 'cubic').
    s <name>            : Saves plot as <name>.png and <name>.pdf, has to be the last param.

    If you want to visualize the difference between two coveragemaps, specify a second result zip file.
    Usage: python viewer2d.py <input.zip> [transmitter] [layer] [<input2.zip [transmitter] [layer]] [-s <name>]

viewer3d.py : Visualizes the map and rays, specify a result zipfile as first argument.
    optional parameters:
    <transmitter>       : Loads rays of specified transmitter.
    Usage: python viewer3d.py <input.zip> [transmitter]

viewerCircleScattered.py : Visualizes the signal strength points on the map, specify a result zipfile as first parameter.
    optional parameters:
    <transmitter>       : Loads rays of specified transmitter.
    -b                  : Draws buildings.
    Usage: python viewerCircleScattered.py <input.zip> [transmitter] [-b]


calculationServer.py : Run this program to receive a calculation task. DO NOT use this and run.py on the same computer.

FOLDER:
src         : Contains all the modules that are used by the software mentioned above.
inputfiles  : Put maps in here.
configfiles : Configure the ray-launching with these files.
ouputfiles  : The outputfile that can be used in ns-3 will be put here.


Additional information for the main program:
Logging:
    Run.py supports five different logging level, which affects, what is stored in the result zipfile.
    Higher level contains all files of lover levels, specify the level in your configuration.
    1 : zipfile contains configuration-files and the result-file for ns3
    2 : adds needed files for 2d-viewer
    3 : adds needed files for 3d-viewer
    4 : stores the whole tmp-folder
    5 : enables debug messages in logfile (might be interesting for developers)

    debugRays: True - adds files to draw rays in 3d-Viewer

Parallel Calculation:
    If you calculate the signal for several transmitter positions, it can be performed parallel:
        -specify the number of cpu-cores under the configuration-key 'numberWorkers'
    You can also calculate the result on several computers. They will be used if you want to calculate rays for more
        transmitter positions than you have cpu-cores
        -specify the ip-addresses of those computers under the configuration-key 'calculationServers'
        -each of those computers has to run calculationServer.py

Map-Files:
    Currently supported are the following formats:
        - City-GML. Please rename your file to <map>.gml
        - Openstreetmap. Please rename your file to <map>.osm
        - files containing polygons. The last and first point should be the same. Please use the file extension 'raw'

Simulation Types:
They are used to describe transmitter and receiver positions
    0 : Point, x y z
    1 : Line,  xs ys zs xe ye ze steps
    2 : Area,  xmin ymin xmax ymax z xstep ystep
    3 : Cubic, xmin ymin zmin xmax ymax zmax xstep ystep zstep
    4 : List,  size x0 y0 z0 ... xn yn zn

    Transmitter positions:
        - if you want to calculate signals for one transmitter (default), set your transmitter position under the
            configuration-key 'transmitters', default is transmitters=[[0,0,1]]
        - if you want to calculate signals for several transmitter, which are ordered in a line, specify a
            transmitter-file as command argument
        - if you want to calculate signals for all transmitter positions on your map, set the configuration-key
            'transmitters' to "area"
            It generates transmitter positions all over the map, the distance between each transmitter is specified in
            configuration-key 'stepSize', the configuration-key 'coverageLevel' describes the height of each transmitter
        - for 3d coverage of your transmitters, set the configuration-key 'transmitters' to 'cubic'.
            It generates transmitter positions all over the map and between 'coverageLevel' and 'coverageMaxLevel' and
            with distance between each position specified in 'stepSize'.
        - if you want to calculate signal for transmitters on specific points, you can either specify them under the
            configuration-key 'transmitters' (transmitters=[[0,0,1],[1,1,1],...]) or in a file as command argument

    Receiver positions:
        - if you want to receive the signal strength in one point, set your receiver position under the configuration-key
            'receivers' (for example: receivers=[[0,0,1]])
        - if you want to place receivers along a line, specify a line in a file and set it as command argument
        - if you want to cover a whole area, set the configuration-key 'receivers' to 'auto' (default)
        - if you want to cover a whole 3d-space, set 'receivers' to 'auto' and make sure that 'coverageMaxLevel' is
            higher than 'coverageLevel'
        - if you want to receive the signal at specific points, you  can either specify them under the configuration-key
            'receivers' (receivers=[[0,0,1],[1,1,1],...]) or in a file as command argument

    Please check the sample files 'sample_lines.tr' and 'sample_list.rec' in the configfolder

Please also check the 'sample.cfg' in the configfolder for further customization.






