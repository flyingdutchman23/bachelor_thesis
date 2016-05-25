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
#ifndef GLOBALS_HPP
#define	GLOBALS_HPP



#define PI 3.14159

#define ACTIVE 0
#define ABORTED 1
#define SUCCEEDED 2


#define UNKNOWN 3
#define MAYBE_RECEIVED 4
#define RECEIVED 5

#define NOTHING 0
#define REFLECTION 1
#define DIFFRACTION 2
#define RECEIVING 3

#define BUFFLEN 500

#define POINT 0
#define LINE 1
#define AREA 2
#define CUBIG 3
#define LIST 4


extern double EPSILON;
extern int RAY_NUM;
extern int MAX_ITERATIONS;
extern double MAX_RANGE;
extern double RECEIVE_THRESHOLD;
extern double DIFFRACTION_THRESHOLD;
extern double REFLECTION_PART;
extern double SCATTERING_PART;
extern double FIRST_ENERGY_THRESHOLD; //no scattering & diffraction if below
extern double WAVELENGTH;
extern double RAY_NUM_DIFFRACTION;
extern double RAY_NUM_SCATTERING;
extern double DEAD_DISTANCE;
extern double TIMEOUT;

extern bool DEBUG;
extern bool SAVERAYS;
extern bool INTERFERENCE;
extern bool PREPROP;




#endif	/* GLOBALS_HPP */

