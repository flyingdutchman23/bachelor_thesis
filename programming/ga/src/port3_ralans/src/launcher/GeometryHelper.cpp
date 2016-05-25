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
#include "GeometryHelper.hpp"
#include "Globals.hpp"

#include "easylogging++.h"

namespace launcher{
   
Vector<double> getNormal(const std::vector<double> &polygons){
    /* working for convex and concave polygons*/
    if(polygons.size() < 9){
        LOG(WARNING) << "Zu wenig Polygone für Normalenberechnung";
        return Vector<double>();
    }
    
    Vector<double> p1(polygons[0], polygons[1], polygons[2]);
    Vector<double> p2(polygons[3], polygons[4], polygons[5]);
    Vector<double> p3(polygons[6], polygons[7], polygons[8]);
    
    Vector<double> n = (p1-p2).cross(p3-p2);
    n.negate();
    n.normalize();
    
    int votesfor = 1;
    int votesagainst = 0;
    int i;
    
    for( i = 0; i < polygons.size()/3 -2; i++){
        Vector<double> p1(polygons[i*3+0], polygons[i*3+1], polygons[i*3+2]);
        Vector<double> p2(polygons[i*3+3], polygons[i*3+4], polygons[i*3+5]);
        Vector<double> p3(polygons[i*3+6], polygons[i*3+7], polygons[i*3+8]);
        Vector<double> n2 = (p1-p2).cross(p3-p2);
        n2.negate();
        if( n*n2 > 0)
            votesfor++;
        else
            votesagainst++;
    }
    
    if (votesagainst > votesfor)
        n.negate();
    
    return n;
    
}

Vector<double> getTriangulatedNormal(const std::vector<double> &polygons){
    
    bool found = true;
    while(polygons.size() > 12 && found){
        found = false;
        int i;
        for(i = 1; i < polygons.size()/3 -1; i++){
            Vector<double> a(polygons[(i-1)*3], polygons[(i-1)*3 +1 ], polygons[(i-1)*3+2]);
            Vector<double> b(polygons[(i)*3], polygons[(i)*3 +1 ], polygons[(i)*3+2]);
            Vector<double> c(polygons[(i+1)*3], polygons[(i+1)*3 +1 ], polygons[(i+1)*3+2]);
            
            if(inPolygon(a, c, polygons)){
                Vector<double> n = (a-b).cross(c-b);
                n.normalize();
                return n;
            }
        }
    }

    Vector<double> a(polygons[0], polygons[1], polygons[2]);
    Vector<double> b(polygons[3], polygons[4], polygons[5]);
    Vector<double> c(polygons[6], polygons[7], polygons[8]);
    Vector<double> n = (a-b).cross(c-b);
    n.normalize();
    return n;
    
}

bool inPolygon(const Vector<double> &a, const Vector<double> &b, const std::vector<double> &polygons){
    if( countRayCrossings( (a+b)/2, Vector<double>(100000, -100000, 100000), polygons) % 2 != 1){
        return false;
    }
    if( countRayCrossings(a,b,polygons) != 0){
        return false;
    }
    return true;
}
    
    
bool getIntersection(const Vector<double> &origin, const Vector<double> &direction, const std::vector<double> &polygon) {
    //This algorithm determines the intersection of a ray with a polygon. Or None if there is no intersection.
    Vector<double> normal = getNormal(polygon);
    
    if (direction*normal == 0) {//catch: ray parallel to face
        return false;
    }
    
    Vector<double> p1(polygon[0], polygon[1], polygon[2]);
    double d = normal*p1;
    double lambda = (d - (origin * normal)) / (direction * normal);
    if (lambda <= 0) {
        return false;
    }
    
    Vector<double> intersect = origin + (direction * lambda); //calculate intersection
    if( countRayCrossings(intersect, Vector<double>(100000,100000,100000), polygon) % 2 == 0){
        return false;
    }

    return true;
}
		
int getIntersection(const Vector<double> &origin, const Vector<double> &direction, const std::vector<double> &polygon, Vector<double> &intersect, Vector<double> &normal) {
	//This algorithm determines the intersection of a ray with a polygon. Or None if there is no intersection.
    normal = getNormal(polygon);
    normal.negate();
    
    Vector<double> p1(polygon[0], polygon[1], polygon[2]);
    double d = normal*p1;
    //catch: ray parallel to face
    if (direction*normal == 0) {
            return -1;
    }
    double lambda = (d - (origin * normal)) / (direction * normal);
    if (lambda <= 0) {
        return -1;
    }
    intersect = origin + (direction * lambda); //calculate intersection
    int cnt =  countRayCrossings(intersect, Vector<double>(100000,100000,100000), polygon);

    if (cnt > 0 && cnt % 2 == 1 ) { //see if the intersection is within the polygon
            return 1;
    }
    return -1;
}

double dapdf(double angle, double slitWidth) {
	//angle-dependent energy density behind a slit, can be used for edges, too, according to "AN IMPROVED ENERGETIC APPROACH TO DIFFRACTION BASED ON THE UNCERTAINTY PRINCIPLE" from Stephenson, Uwe
	double v = 2.0 * slitWidth * angle;
	return 1.0 / (1.0 + 2.0 * v * v) ;
}

double getAngle(const Vector<double> &a, const Vector<double> &b) {
	double num = a * b;
	num = num < 0 ? -num : num;
	double denum = a.length() * b.length();
	return acos(num/denum);
}

int countRayCrossings2D(const Vector<double> &a, const Vector<double> &b, const std::vector<double> &polygon, int dim1, int dim2) {
	//This algorithm determines the number of intersections of a line from a to b with the polygon, where dim1 and dim2 denote a 2d-projection.
	
	int count=0;
	for (int i=1; i < polygon.size()/3; i++) {
		Vector<double> c(polygon[(i-1)*3],polygon[(i-1)*3+1],polygon[(i-1)*3+2]);
		Vector<double> d(polygon[i*3],polygon[i*3+1],polygon[i*3+2]);
	
		//print "check crossing:", a,b,c,d,dim1,dim2
		//calculation of intersection according to i=a+lambda*(b-a)=c+tau*(d-c) with reduction to 2 dimesnions (this keeps the topology)
		if((b[dim1]-a[dim1])==0 || ((d[dim1]-c[dim1])*(b[dim2]-a[dim2])/(b[dim1]-a[dim1])-d[dim2]+c[dim2])==0 ) return -1; //check all denominators
		double tau= (c[dim2] - a[dim2]  - (c[dim1] - a[dim1]) * (b[dim2] - a[dim2]) / (b[dim1]-a[dim1]) ) / 
                          ( (d[dim1] - c[dim1]) * (b[dim2] - a[dim2]) / (b[dim1] - a[dim1]) - d[dim2]+c[dim2] );
		double lamda=(c[dim1]+tau*(d[dim1]-c[dim1])-a[dim1])/(b[dim1]-a[dim1]);
		if ( (tau > EPSILON && tau <1-EPSILON && lamda >= 0 && lamda <= 1) || (lamda > EPSILON && lamda <1-EPSILON && tau >= 0 && tau <= 1) ) 
			count+=1;
	}
	return count;
}

int countRayCrossings(const Vector<double> &a, const Vector<double> &b, const std::vector<double> &polygon) {
	//This algorithm determines the number of intersections of a line from a to b with the polygon.
	
	//The check is performed in only two dimensions, this is allowed because the projection doesn't change the topology.
	//A valid projection is determined by just trying it with xy, the xz and the yz plane.
	int res = countRayCrossings2D(a,b,polygon,0,1);
	if (res < 0) {
		res = countRayCrossings2D(a,b,polygon,0,2);
		if (res < 0) {
			res = countRayCrossings2D(a,b,polygon,1,2);
			if (res < 0) {
				LOG(DEBUG) << "something went wrong - inPolygon-check failed in all projections";
			}
		}
	}
	return res;
}
}