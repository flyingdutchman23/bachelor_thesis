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
#ifndef GEOMETRYHELPER_HPP
#define	GEOMETRYHELPER_HPP

#include "Vector.hpp"
#include <vector>

namespace launcher{
    
    Vector<double> getNormal(const std::vector<double> &polygon);
    Vector<double> getTriangulatedNormal(const std::vector<double> &polygons);
    
    bool inPolygon(const Vector<double> &a, const Vector<double> &b, const std::vector<double> &polygons);
    
    bool getIntersection(const Vector<double> &origin, const Vector<double> &direction, const std::vector<double> &poylgon);
    int getIntersection(const Vector<double> &origin, const Vector<double> &direction, const std::vector<double> &polygon, Vector<double> &intersect, Vector<double> &normal);
    
    int countRayCrossings2D(const Vector<double> &a, const Vector<double> &b, const std::vector<double> &polygon, int dim1, int dim2);
    int countRayCrossings(const Vector<double> &a, const Vector<double> &b, const std::vector<double> &polygon);

    double dapdf(double angle, double slitWidth);
    double getAngle(const Vector<double> &a, const Vector<double> &b);
    
}
#endif	/* GEOMETRYHELPER_HPP */

