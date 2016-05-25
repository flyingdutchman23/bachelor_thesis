
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
from OpenGL.GL import shaders
from OpenGL.GL import *
import pygame
from ctypes import *
from OpenGL.GLU import *
import numpy as np
import time
from sys import exit
import marshal
import sys
import zipfile

from .src.globals import mkdir
from .src.globals import rmdir


size = width, height = 1600, 900
SIGMA = 1e-10

#COLOR_TABLE=[(1,1,1,1),(0,0.4,0,1),(0,0,0,0)]
#SHADER_TABLE=[0,0,1]

#TYPE_TABLE=[GL_TRIANGLES, GL_TRIANGLES, GL_POINTS]
#print len(TYPE_TABLE)

shader_table = []
color_table  = []
type_table   = []

class Rendering():
    def init(self):
        self.theta = np.pi / 2.0
        self.phi = 1.0
        self.r = 100.0
        self.new_rotate = True
        self.new_shift = True
        self.aim = [0, 0, 0]

        pygame.init()
        screen = pygame.display.set_mode(size, pygame.OPENGL | pygame.DOUBLEBUF, 16)
        glClearColor(1, 1, 1, 1.0)

        glMatrixMode(GL_PROJECTION)
        gluPerspective(60, 1.0 * width / height, 5.0, 30000.0)
        glMatrixMode(GL_MODELVIEW)
        #glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        VERTEX_SHADER = shaders.compileShader("""
				varying vec3 fragmentNormal;
				void main() {
					gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
					gl_FrontColor = gl_Color; 
					fragmentNormal = gl_Normal;
				}
			""", GL_VERTEX_SHADER)
        FRAGMENT_SHADER = shaders.compileShader("""
				varying vec3 fragmentNormal;
				void main() {
					//gl_FragColor = vec4( 0, 1, 0, 1 );
					//vec3 ambient=vec3(0.1,0.1,0.1);
					vec3 ambient=0.1*vec3(gl_Color.r,gl_Color.g,gl_Color.b);
					vec3 lightdir=normalize(vec3(-1.0,-1.0,-1.0));
					//vec3 lighting=(clamp(dot(fragmentNormal,lightdir),-1,1)+1.0)/2.0*vec3(1.0,1.0,1.0);
					vec3 lighting=(clamp(dot(fragmentNormal,lightdir),-1,1)+1.0)/2.0*vec3(gl_Color.r,gl_Color.g,gl_Color.b);
					gl_FragColor = vec4(ambient+lighting,1);
					//gl_FragColor = gl_Color;
				}
			""", GL_FRAGMENT_SHADER)
        self.shader = [shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER)]


        VERTEX_SHADER = shaders.compileShader("""
				varying vec3 fragmentNormal;
				void main() {
					gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
					gl_FrontColor = gl_Color;
					fragmentNormal = gl_Normal;
				}
			""", GL_VERTEX_SHADER)
        FRAGMENT_SHADER = shaders.compileShader("""
				varying vec3 fragmentNormal;
				void main() {
					gl_FragColor = vec4(fragmentNormal,1.0f);
				}
			""", GL_FRAGMENT_SHADER)
        self.shader.append(shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER))


    def getFaces(self, zipf, reqTr = None):
        print("Transmitter given: ", reqTr)


        tmp = 'v3d-tmp/'
        rmdir(tmp)
        mkdir(tmp)

        try:
            zf = zipfile.ZipFile(zipf, 'r')
        except IOError:
            print("Could not find archiv: ", zipf)
            sys.exit()

        cfgf = 'config.vcfg'
        try:
            cfgfile = zf.open(cfgf)
        except KeyError:
            print("Could not find configfile", cfgf, "in archiv:", zipf)
            sys.exit()

        binfilenames = []
        print("loading vertices...")
        reqTrFound = False
        for line in cfgfile:
            line = line.split("#")[0]
            binf = line.split('\t')[0]
            if reqTr != "all" and "rays" in line:
                tr = eval(line.split('/')[-1].split('.bin')[0])
                #print tr, np.linalg.norm(np.array(reqTr) - np.array(tr))
                if reqTr is not None and np.linalg.norm(np.array(reqTr) - np.array(tr)) < 0.1:
                    print("Found transmitter:", tr)
                    reqTrFound = True
                else:
                    continue
            try:
                zf.extract(binf, tmp)
            except KeyError:
                print("Could not find binaryfile", binf, "in archiv:", zipf)
                sys.exit()
            arr = line.split("\t")
            if len(arr) == 4:
                binfilenames.append(tmp+arr[0].strip())
                color_table.append(eval(arr[1].strip()))
                shader_table.append(int(arr[2].strip()))
                type_table.append(eval(arr[3].strip()))
                self.vertices = []
                for binfilename in binfilenames:
                    try:
                        f = open(binfilename, "rb")
                    except IOError:
                        print("Could not find binary file:", binfilename, '\n Exiting...')
                        sys.exit()
                    vertices = marshal.load(f)
                    self.vertices.append(vertices)
                    f.close()
        print("...done")
        if not reqTrFound:
            if reqTr is None:
                print("No transmitter given, viewing buildings.")
            if reqTr != 'all':
                print("Transmitter not found, viewing buildings.")

        cfgfile.close()
        zf.close()

        self.vbos = []
        for vertices in self.vertices:
            vbo = glGenBuffers(1)
            self.vbos.append(vbo)
            glBindBuffer(GL_ARRAY_BUFFER, vbo)
            glBufferData(GL_ARRAY_BUFFER, len(vertices) * 4, (c_float * len(vertices))(*vertices), GL_STATIC_DRAW)

    def render(self):
        t = time.time()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        if pygame.mouse.get_pressed()[0] == 1:
            mpos = pygame.mouse.get_rel()
            if not self.new_rotate:
                self.phi -= mpos[0] / 100.0
                self.theta += mpos[1] / 100.0
                if self.theta < SIGMA:
                    self.theta = SIGMA
                if self.theta > np.pi:
                    self.theta = np.pi
            else:
                self.new_rotate = False
        else:
            self.new_rotate = True
        if pygame.mouse.get_pressed()[2] == 1:
            mpos = pygame.mouse.get_rel()
            if not self.new_shift:
                #project view in xy plane and normalize
                vec = np.array(self.aim) - np.array(self.camera)
                vec = vec[0:2]
                vec = vec / np.linalg.norm(vec)
                tmp = vec * mpos[1]
                vec = np.array([-vec[1], vec[0]])  #rotate
                tmp += vec * mpos[0]
                self.aim[0] += tmp[0]
                self.aim[1] += tmp[1]

            else:
                self.new_shift = False
        else:
            self.new_shift = True

        self.camera = [self.aim[0] + self.r * np.sin(self.theta) * np.cos(self.phi),
                       self.aim[1] + self.r * np.sin(self.theta) * np.sin(self.phi),
                       self.aim[2] - self.r * np.cos(self.theta)]
        gluLookAt(self.camera[0], self.camera[1], self.camera[2],
                  self.aim[0], self.aim[1], self.aim[2],
                  0, 0, 1)
        """Render the geometry for the scene."""

        try:
            #self.vbo.bind()
            try:
                glEnableClientState(GL_VERTEX_ARRAY);
                glEnableClientState(GL_NORMAL_ARRAY);

                #glBindBuffer (GL_ARRAY_BUFFER, self.vbo)
                i = 0
                for vbo, vertices in zip(self.vbos, self.vertices):
                    shaders.glUseProgram(self.shader[shader_table[i]])
                    glBindBuffer(GL_ARRAY_BUFFER, vbo)
                    #glVertexPointerf( 1 )
                    glColor(color_table[i])
                    glEnable(GL_LINE_SMOOTH)
                    glLineWidth(3.0)
                    glVertexPointer(3, GL_FLOAT, 24, None)
                    glNormalPointer(GL_FLOAT, 24, c_void_p(12))
                    glDrawArrays(type_table[i], 0, int(len(vertices) / 3))

                    i += 1
                #-----
                #glVertexPointerf( vbo )
                #glVertexPointer (3, GL_FLOAT, 24, None)
                #glNormalPointer (GL_FLOAT, 24, c_void_p(12))
                #glDrawArrays(GL_TRIANGLES, 0, int(len(self.vertices)/3))
            finally:
                #self.vbo.unbind()
                glDisableClientState(GL_VERTEX_ARRAY);
        finally:
            shaders.glUseProgram(0)

    def getEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.r *= 0.9
                if event.button == 5:
                    self.r *= 1.1


if __name__ == "__main__":

    if sys.argv[1].split('.')[-1] != 'zip':
        print("Invalid inputfiletype, required zipfile! \n Usage: python viewer3d.py <input.zip> [transmitter | all]")
        sys.exit()

    r = Rendering()
    r.init()
    reqTr = None
    if len(sys.argv) == 3:
        if sys.argv[2] == 'all':
            reqTr = sys.argv[2]
        else:
            try:
                reqTr = eval(sys.argv[2])
            except:
                print("Invalid transmitter:", sys.argv[2])
    r.getFaces(sys.argv[1], reqTr)
    while True:
        r.render()
        pygame.display.flip()
        r.getEvents()
