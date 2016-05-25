
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


blub = subprocess.check_output(['./launcher',
                                "../../tmp/polygons/small_street_buildings.txt",
                                "../../tmp/polygons/small_street_terrain.txt",
                                "../../tmp/edges/small_street_buildings.txt",
                                "../../tmp/edges/small_street_terrain.txt", "../../tmp/rays/small_street.txt",

                                "-50", "50",  # RECEIVER : X
                                "-30", "20",  #RECEIVER : Y
                                "-2", "-2",  #RECEIVER : Z
                                "1",  #STEPWIDTH
                                "0", "0", "-2",  #TRANSMITTER
                                "10000",  #RAY_NUM
                                "50",  #MAX_ITERATIONS
                                "1.0",  #RECEIVE_THRESHOLD
                                "0.0",  #DIFFRACTION_THRESHOLD
                                "0.3",  #REFLECTION_PART
                                "0.125",  #WAVELENGTH
                                "0",  #INTERFERENCE
                                "100",  #RAY_NUM_DIFFRACTION
                                "100",  #RAY_NUM_SCATTERING
                                "1",  #DEBUG
                                "0.5",  #DEAD_DISTANCE
                                "0.0",  #SCATTERING_PART
                                "60.0"])  # TIMEOUT
print(blub)

# makeViewable.makeViewable("../../tmp/rays/small_street.txt","../../tmp/rays/small_street.bin")

