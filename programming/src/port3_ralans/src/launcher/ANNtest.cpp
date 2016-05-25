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
 * File:   mainANN.cpp
 * Author: jonas
 *
 * Created on 14. April 2015, 15:36
 */

#include <cstdlib>

#include <ANN/ANN.h>

#include "Vector.hpp"
#include <vector>
#include <fstream>
#include <sstream>


int k = 2; // number of nearest neighbors
int dim = 3; // dimension
double eps = 0; // error bound


void createPoints(launcher::Vector<double> v, ANNpoint p){
    for(int i=0; i<dim; i++){
        p[i] = v[i];
    }
}

std::vector<launcher::Vector<double> > parseList(char* filename){    
    std::ifstream infile;
    infile.open(filename);
    if(infile.fail()){
        std::cout << "Cant open " << filename << std::endl;;
        exit(1);
    }
    
    std::string temp;
    std::vector<launcher::Vector<double> > receivers;
    while(std::getline(infile, temp)){
        std::istringstream ss(temp);
        double x,y,z;
        ss >> x >> y >> z;
        receivers.push_back(launcher::Vector<double>(x,y,z));
    }
    return receivers;
    
}

std::string printPt(ANNpoint p) // print point
{
    std::stringstream ss;
    ss << "(" << p[0];
    for (int i = 1; i < dim; i++) {
        ss << ", " << p[i];
    }
    ss << ")";
    return ss.str();
}


int main(int argc, char** argv) {

    std::cout << "Create kd_tree Pointer" << std::endl;
    ANNkd_tree *kdt;
    int nPoints = 0;
    
    std::vector<launcher::Vector<double> >points;
    points = parseList(argv[1]);
    
    nPoints = points.size();
    
    std::cout << "Punkte: " << nPoints << std::endl;
    ANNpointArray dataPoints = annAllocPts(nPoints, dim);
    ANNidxArray nnIdx = new ANNidx[k];
    ANNdistArray dists = new ANNdist[k];
    
    std::cout << "Create Points" << std::endl;
    for(int i=0; i<nPoints; i++){
        createPoints(points[i], dataPoints[i]); 
    }
    
    std::cout << "Create kd_tree" << std::endl;
    kdt = new ANNkd_tree(dataPoints, nPoints, dim);
    
    std::cout << "Points in kdt: " << kdt->nPoints() << std::endl;
    std::cout << "Dim of kdt: " << kdt->theDim() << std::endl;
    std::cout << "P-DP: "<< dataPoints << " | P-KDT-DP: " << kdt->thePoints() << std::endl;
    
    std::cout << "Create query Point" << std::endl;
    ANNpoint queryPt = annAllocPt(dim);
    createPoints(launcher::Vector<double>(1,1,1), queryPt);
    
    std::cout << "Perfom query" << std::endl;
    kdt->annkSearch(queryPt, k, nnIdx, dists, eps);        
    std::cout << "\tNN:\tIndex\tDistance" << std::endl;;
        for (int i = 0; i < k; i++) { // print summary
            dists[i] = sqrt(dists[i]); // unsquare distance
            std::cout << "\t" << i << "\t" << nnIdx[i] << "\t" << dists[i] << "\n";
        }
    std::cout << "Nearest-Point:" << printPt(dataPoints[nnIdx[0]]) << " | Query-Point:"<< printPt(queryPt) << std::endl;
    
    //std::cout << "Print kd_tree" << std::endl;
    //std::ostream out(std::cout.rdbuf());
    //kdt->Print(ANNfalse, out);
    //std::cout << out;
    
    delete [] nnIdx;
    delete [] dists;
    delete kdt;
    annClose();
 
    return 0;
}
