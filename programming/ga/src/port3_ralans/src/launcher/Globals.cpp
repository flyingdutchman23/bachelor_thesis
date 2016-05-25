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
#include "Globals.hpp"

double EPSILON = 0.000001;
int RAY_NUM = 1000;
int MAX_ITERATIONS = 50;
double RECEIVE_THRESHOLD = 1;
double DIFFRACTION_THRESHOLD = 0.0;
double REFLECTION_PART = 1.0;
double SCATTERING_PART = 0.0;
double FIRST_ENERGY_THRESHOLD = 1e-4; //no scattering & diffraction if below
double WAVELENGTH = 3e8 / 2.4e9;
double RAY_NUM_DIFFRACTION = 100;
double RAY_NUM_SCATTERING = 100;
double DEAD_DISTANCE = 0.5;
double TIMEOUT = 10.0;
double MAX_RANGE = 0;

bool PREPROP = false;
bool DEBUG = false;
bool SAVERAYS = false;
bool INTERFERENCE = false;

    