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
#include "Ray.hpp"

namespace launcher{

Ray::Ray(	double origin_x, double origin_y, double origin_z,
		double direction_x, double direction_y, double direction_z,
		double energy_arg, int status_arg, double total_distance, int num_reflections, int predecessor) {
	//direction = {origin_x, origin_y, origin_z};
	origin = Vector<double>(origin_x, origin_y, origin_z);
	direction = Vector<double>(direction_x, direction_y, direction_z);
	energy=energy_arg;
	status=status_arg;
	totalDistance=total_distance;
	numReflections=num_reflections;
	this->predecessor = predecessor;
}


void Ray::print() const{
	std::cout << origin[0] << " " << origin[1] << " " << origin[2] << " -> " << direction[0] << " " << direction[1] << " " << direction[2] << " energy: " << energy << std::endl;
}

void Ray::print2file(std::ofstream &stream) const{
	stream << origin[0] << " " << origin[1] << " " << origin[2] << " " << direction[0] << " " << direction[1] << " " << direction[2] << " " << energy << " " << status << std::endl;
}



void print_rays(const std::vector<Ray> &rays) {
	std::vector<Ray>::size_type sz = rays.size();
	for (int i=0; i<sz; i++) {
		rays[i].print();
	}
}

void save_rays(const std::vector<Ray> &rays, const std::string &folder, const Vector<double> &tr) {
    std::string filename = folder + tr.toString() + ".txt";
    std::ofstream myfile (filename.c_str());
    std::vector<Ray>::size_type sz = rays.size();
    for (int i=0; i<sz; i++) {
            rays[i].print2file(myfile);
    }
    myfile.close();
}

}