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
#ifndef VECTOR_HPP
#define	VECTOR_HPP

#include <iostream>
#include <iomanip>


#define TOLERANCE 0.00000000000000000000000000000000000000000000001

namespace launcher{

template<typename T>
class Vector {
    
public:
    Vector();
    Vector(T x, T y, T z);
    
    void normalize();
    T length() const;
    void negate();
    Vector rotate(const Vector axis, double angle) const;
    
    Vector cross(const Vector v) const;
    
    Vector operator+ (const Vector v) const;
    void operator+= (const Vector v);
    Vector operator- (const Vector v) const;
    Vector operator* (const T scale) const;
    void operator*= (const T scale);
    T operator* (const Vector v) const;
    Vector operator/ (const T scale) const;
    void operator/= (const T scale);
    T distance(const Vector v) const;
    
    
    T operator[] (const int& index) const;
    
    std::string toString() const;
    
    T x, y, z;
private:

};

template<typename T>
std::ostream& operator<<(std::ostream &out, const Vector<T> &v){
    return out << std::setprecision(6) << "[" << v.x << ", " << v.y << ", " << v.z << "]";
}

}
#include "Vector.tcc"

#endif	/* VECTOR_HPP */

