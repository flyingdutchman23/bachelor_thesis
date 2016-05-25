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
/* 
 * File:   IOHelper.cpp
 * Author: jonas
 * 
 * Created on 17. August 2015, 12:13
 */

#include "IOHelper.hpp"

#include "easylogging++.h"


namespace launcher{


/**
* Parses file with space-seperated coordinates into a 3d vector.
**/
std::vector<std::vector<double> > parseFile (std::string filename) {
	std::ifstream infile;
	infile.open (filename.c_str());
	if (infile.fail()) {
		LOG(WARNING) << "Can't open "<< filename;
		exit(1);
	}
	std::vector<std::vector<double> > numbers;

	std::string temp, tmp;

	while(std::getline(infile, temp)) {
		std::istringstream buffer(temp);
		std::vector<double> line;
		double d;
		while (getline( buffer, tmp, ' ' )) {
			d = atof(tmp.c_str());
			line.push_back(d);
		}
		
		numbers.push_back(line);
	}
	infile.close();

	return numbers;
}

void saveEdges(const std::string &filename, const std::vector<std::vector<double> > &edges){
        
    std::ofstream edgefile (filename.c_str());
    edgefile << std::scientific << std::setprecision(18);
	for(int i = 0; i<edges.size(); i++){
		std::vector<double>::size_type sz = edges[i].size();

		for (int j=0; j<sz; j++) {
			edgefile << edges[i][j] << " ";
		}
        edgefile << std::endl;
    }
    edgefile.close();
}

}
