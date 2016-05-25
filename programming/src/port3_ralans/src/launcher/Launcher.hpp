//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Copyright (c) 2015, University of Osnabrueck                                                                         //
//   All rights reserved.                                                                                               //
//                                                                                                                      //
//   Redistribution and use in source and binary forms, with or without modification, are permitted provided that the   //
//   following conditions are met:                                                                                      //
//                                                                                                                      //
//   1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following//
//       disclaimer.                                                                                                    //
//                                                                                                                      //
//   2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the       //
//       following disclaimer in the documentation and/or other materials provided with the distribution.               //
//                                                                                                                      //
//   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, //
//   INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE  //
//   DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, //
//   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR    //
//   SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,  //
//   WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE   //
//   USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.                                           //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#ifndef LAUNCHER_HPP
#define LAUNCHER_HPP

#include <vector>
#include "Ray.hpp"

namespace launcher{
 
/**
* Parses file with space-seperated files into a 2d vector.
**/
//std::vector<std::vector<double> > parseFile (std::string filename);

/**
  * Launch new rays from 'origin'. 'total_energy' is distributed equally on these rays. With active & normal subspace can be excluded from ray launching (when there is a wall).
  **/
void launch_rays(std::vector<Ray> * rays, Vector<double> origin, double total_energy, bool active1, Vector<double> normal1, bool active2, Vector<double> normal2, double totalDistance, int numReflections,int predecessor, int numRays);

/**
  * launches a scattered ray in a random direction
  **/
void doScattering(std::vector<Ray> * rays, Vector<double> origin, double energy, Vector<double> normal, double totalDistance, int numReflections, int predecessor);
void checkDiffraction(Ray ray, int &eventtype, double &eventdistance, Vector<double> &eventconnection, Vector<double> &eventedge, Vector<double> &eventnormal1, Vector<double> &eventnormal2, double &eventslitwidth, std::vector<double> edge, double WAVELENGTH, double DIFFRACTION_THRESHOLD, double DEAD_DISTANCE);
void doDiffraction(Vector<double> eventconnection, Vector<double> eventedge, double eventslitwidth, double eventdistance, Vector<double> eventnormal1, Vector<double> eventnormal2, Ray ray, int NUMRAYS, std::vector<Ray> &newrays, int predecessor);


double getEnergy(const Vector<double> &receiver, const std::vector<Ray> &rays, const Vector<double> &transmitter);

std::string getIdentifier(const std::string &filename);
std::string getTmpFolder(const std::string &filename);
std::string getWorkFolder(const std::string &filename);
Vector<double> getTransmitter(const std::string &workfolder, const int &id, double &rt);

int parseType(const std::string&, double &xmin, double &xmax, double &ymin, double &ymax, double &zmin, double &zmax, double &lx, double &ly, double &lz, int &t);
std::vector<Vector<double> >parseReceiverListFile(const std::string &filename);
std::vector<Vector<double> >parseReceiverLineFile(const std::string &filename);
}

#endif /* LAUNCHER_HPP */