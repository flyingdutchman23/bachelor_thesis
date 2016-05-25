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

#include <cstdlib>
#include <vector>
#include <string>

#include "IOHelper.hpp"
#include "GeometryHelper.hpp"


#include "easylogging++.h"

_INITIALIZE_EASYLOGGINGPP

using namespace launcher;


std::vector<std::vector<double> > extractEdges(const std::vector<std::vector<double> > &buildingsPolygons);

int main (int argc, char* argv[]) {


    if (argc != 2){
        std::cout << "wrong number of arguments, requires exactly 1" << std::endl;
        exit(42);
    }
    
    std::string workFolder(argv[1]);
    std::string buildingsPolygons = workFolder + "polygons/buildings.txt";
    std::string terrainPolygons   = workFolder + "polygons/terrain.txt";
    std::string buildingsEdges    = workFolder + "edges/buildings.txt";
    std::string terrainEdges      = workFolder + "edges/terrain.txt";
    std::string logFile           = workFolder + "logs/edge.log";
    
    std::time_t starttime, currenttime;
    double runtime;
    
    easyloggingpp::Configurations conf;
    conf.setAll(easyloggingpp::ConfigurationType::ToFile, "true");
    conf.setAll(easyloggingpp::ConfigurationType::ToStandardOutput, "false");
    conf.setAll(easyloggingpp::ConfigurationType::Filename, logFile);
    conf.setAll(easyloggingpp::ConfigurationType::Format, "%datetime %level %log");
    conf.set(easyloggingpp::Level::Warning, easyloggingpp::ConfigurationType::ToStandardOutput, "true");
    conf.set(easyloggingpp::Level::Warning, easyloggingpp::ConfigurationType::Format, "%datetime %level %log [%func]");
    easyloggingpp::Loggers::reconfigureLogger("default", conf);
    easyloggingpp::Loggers::reconfigureAllLoggers(conf);
    
    //load polygons and edges
    LOG(INFO) << "Workingdir: " << workFolder;
    //LOG(INFO) << "Identifier: " << identifier;
    LOG(INFO) << "Parsing files:";
    LOG(INFO) << buildingsPolygons;
    std::vector<std::vector<double> > polygons =parseFile(buildingsPolygons);
    LOG(INFO) << terrainPolygons;
    std::vector<std::vector<double> > polygons2 =parseFile(terrainPolygons);
    LOG(INFO) << "Buildingpolygons parsed: " << polygons.size();
    LOG(INFO) << "Terrainpolygons parsed: " << polygons2.size();
    for (int i=0; i < polygons2.size(); i++) {
        polygons.push_back(polygons2[i]);
    }
    
    //extract edges
    std::time(&starttime);
    LOG(INFO) << "Extracting edges...";
    std::vector<std::vector<double> > edges, edges2;
    edges  = extractEdges(polygons);
    edges2 = extractEdges(polygons2);
    std::time(&currenttime);
    runtime = currenttime - starttime;
    LOG(INFO) << "Extracted edges in " << runtime << " seconds.";
    LOG(INFO) << "Buildingedges found: " << edges.size();
    LOG(INFO) << "Terrainedges found: " << edges2.size();
    
    LOG(INFO) << "Saving edges.";
    saveEdges(buildingsEdges, edges);
    saveEdges(terrainEdges, edges2);
    
    LOG(INFO) << "Finished...";
        
     
    return EXIT_SUCCESS;
}

    
std::vector<std::vector<double> > extractEdges(const std::vector<std::vector<double> > &polygons){
    
    std::time_t stime, ctime;
    LOG(INFO) << "poylgonsize: " << polygons.size();
    LOG(INFO) << "extract edges...";
    std::time(&stime);
    
    std::vector<std::vector<double> > edges;
    
    int i, j, nextpg, currpg;
    for(currpg = 0; currpg < polygons.size(); currpg++){
        std::vector<double> polygon = polygons[currpg];
        for(i = 0; i < polygon.size()/3 -1; i++){
            Vector<double> e1 (polygon[i*3+0],polygon[i*3+1],polygon[i*3+2]);
            Vector<double> e2 (polygon[i*3+3],polygon[i*3+4],polygon[i*3+5]);
            
            bool foundedge = false;
            
            for(nextpg = currpg +1; nextpg < polygons.size(); nextpg++){
                std::vector<double> polygon2 = polygons[nextpg];
                
                for(j = 0; j < polygon2.size()/3 -1; j++){
                    Vector<double> eb1 (polygon2[j*3+0],polygon2[j*3+1],polygon2[j*3+2]);
                    Vector<double> eb2 (polygon2[j*3+3],polygon2[j*3+4],polygon2[j*3+5]);
                                        
                    
                    if( ( (eb2-e1)*(eb2-e1) == 0 && (eb1-e2)*(eb1-e2) == 0 ) || 
                        ( (eb1-e1)*(eb1-e1) == 0 && (eb2-e2)*(eb2-e2) == 0 ) ){
                        Vector<double> n1 = getNormal(polygon);
                        Vector<double> n2 = getNormal(polygon2);
                        
                        
                        if( n1*n2 < 0.95 ){
                            Vector<double> p = (e1 + e2) / 2 + (n1 + n2) * 0.01;
                            
                            if( !getIntersection(p, n1*(-1), polygon) &&
                                !getIntersection(p, n2*(-1), polygon2) ){
                                std::vector<double> edge;
                                edge.push_back(polygon[i*3+0]);
                                edge.push_back(polygon[i*3+1]);
                                edge.push_back(polygon[i*3+2]);
                                edge.push_back(polygon[i*3+3]);
                                edge.push_back(polygon[i*3+4]);
                                edge.push_back(polygon[i*3+5]);
                                edge.push_back(n1[0]);
                                edge.push_back(n1[1]);
                                edge.push_back(n1[2]);
                                edge.push_back(n2[0]);
                                edge.push_back(n2[1]);
                                edge.push_back(n2[2]);
                                edges.push_back(edge);
                                foundedge = true;
                            }     
                        }
                    }
                }
                if( foundedge ){
                    break;
                }
            }
        }
    }
    
    std::time(&ctime);
    LOG(INFO) << "extracted edges in " << ctime - stime << " seconds";
    LOG(INFO) << "edges found: " << edges.size();
    
    return edges;
}
