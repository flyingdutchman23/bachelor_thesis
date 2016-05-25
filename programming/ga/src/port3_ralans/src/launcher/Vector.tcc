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
#ifndef VECTOR_TCC
#define	VECTOR_TCC

#include "Vector.hpp"
#include <sstream>
#include <cmath>

namespace launcher{
    

template<typename T>
Vector<T>::Vector(){
    x = y = z = 0.0;
}

template<typename T>
Vector<T>::Vector(T _x, T _y, T _z){
    x = _x;
    y = _y;
    z = _z;
}

template<typename T>
void Vector<T>::normalize(){
    T tmp = x*x + y*y + z*z;
    
    if( fabs(tmp - 1.0f) > TOLERANCE){
        T mag = sqrt(tmp);
        x /= mag;
        y /= mag;
        z /= mag;
    }
}

template<typename T>
T Vector<T>::length() const{
    T tmp = x*x + y*y + z*z;
    return sqrt(tmp);
}

template<typename T>
void Vector<T>::negate(){
    x*=-1;
    y*=-1;
    z*=-1;
}

template<typename T>
Vector<T> Vector<T>::rotate(const Vector axis, double angle) const{
    double cosa = cos(angle);
    double sina = sin(angle);
    T ax = axis[0];
    T ay = axis[1];
    T az = axis[2];
    
    T tx = (ax * ax * (1 - cosa) + cosa) * x  +  (ax * ay * (1 - cosa) - az * sina) * y  +  (ax * az * (1 - cosa) + ay * sina) * z;
    T ty = (ay * ax * (1 - cosa) + az * sina) * x  +  (ay * ay * (1 - cosa) + cosa) * y  +  (ay * az * (1 - cosa) - ax * sina) * z;
    T tz = (az * ax * (1 - cosa) - ay * sina) * x  +  (az * ay * (1 - cosa) + sina * ax) * y  +  (az * az * (1 - cosa) + cosa) * z;
	
    return Vector<double>(tx, ty, tz);
}

template<typename T>
Vector<T> Vector<T>::cross(const Vector v) const{
    
    T tx = y*v.z - z*v.y;
    T ty = z*v.x - x*v.z;
    T tz = x*v.y - y*v.x;
    
    return Vector<T>(tx, ty, tz);
}


template<typename T>
Vector<T> Vector<T>::operator +(const Vector v) const{
    T tx = x + v.x;
    T ty = y + v.y;
    T tz = z + v.z;
    return Vector<T>(tx, ty, tz);
}

template<typename T>
void Vector<T>::operator +=(const Vector v){
    x += v.x;
    y += v.y;
    z += v.z;
}

template<typename T>
Vector<T> Vector<T>::operator -(const Vector v) const{
    T tx = x - v.x;
    T ty = y - v.y;
    T tz = z - v.z;
    return Vector<T>(tx, ty, tz);
}

template<typename T>
Vector<T> Vector<T>::operator *(const T scale) const{
    T tx = x * scale;
    T ty = y * scale;
    T tz = z * scale;
    return Vector<T>(tx, ty, tz);
}

template<typename T>
void Vector<T>::operator *=(const T scale){
    x *= scale;
    y *= scale;
    z *= scale;
}

template<typename T>
T Vector<T>::operator *(const Vector v) const{
    return (x*v.x + y*v.y + z*v.z);
}

template<typename T>
Vector<T> Vector<T>::operator /(const T scale) const{
    return Vector<T>(x/scale, y/scale, z/scale);
}

template<typename T>
void Vector<T>::operator /=(const T scale){
    x/=scale;
    y/=scale;
    z/=scale;
}

template<typename T>
T Vector<T>::operator [](const int& index) const{
    switch (index){
        case 0: 
            return x;
            break;
        case 1: 
            return y;
            break;
        case 2: 
            return z;
            break;
        default:
            std::cout << "Invalid range for vector: " << index << " - vector has only 3 dimensions" << std::endl;
            return 0.;
    }
}

template<typename T>
std::string Vector<T>::toString() const{
    std::ostringstream ss;
    ss << std::setprecision(6) << "[" << x << ", " << y << ", " << z << "]";
    return ss.str();
}

template<typename T>
T Vector<T>::distance(const Vector v) const{
    return (v - *this).length();
}

}
#endif	/* VECTOR_TCC */

