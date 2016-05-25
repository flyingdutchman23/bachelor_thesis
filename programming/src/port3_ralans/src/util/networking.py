
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
import socket
import time
import sys
import src.globals as gl


TCP_PORT = 4242
BUFFER_SIZE = 4096

DATA_TAG = 's'
RETRY_TIME = 2


def startLinkServer(port = None):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    gl.logger.info("hostname: " + str(socket.gethostname()))
    s.bind(('', TCP_PORT if port is None else port))
    s.listen(1)
    conn, addr = s.accept()
    return s, conn


def stopLinkServer(s, conn):
    conn.close
    s.close


def receive(conn):
    gl.logger.debug("incomming data, BUFFERSIZE: " + str(BUFFER_SIZE))
    received = ""
    needed = 11;
    while needed != 0:
        data = conn.recv(needed)
        recvlen = len(data)
        needed -= recvlen
    gl.logger.debug("recv: " + data[0] + data[1:])

    datalen = int(data[1:11])
    gl.logger.debug("receive: " + str(datalen))

    while datalen != 0:
        recvlen = BUFFER_SIZE
        if(datalen < BUFFER_SIZE):
            recvlen = datalen
        gl.logger.debug("data to receive: " + str(datalen))

        data = conn.recv(recvlen)
        gl.logger.debug("data received: " + str(len(data)))
        datalen -= len(data)
        received += data
    return received


def send(data, s):
    lenstr = "%010d" % len(data)
    gl.logger.debug("sending " + str(len(data)))
    s.send(DATA_TAG + lenstr + data)


def startLinkClient(hostname, retry, port = None):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    success = False
    while True:
        try:
            time.sleep(RETRY_TIME)
            s.connect((hostname,  TCP_PORT if port is None else port))
            return s
        except Exception as e:
            if not retry:
                print(e)
                sys.exit(2)
				
