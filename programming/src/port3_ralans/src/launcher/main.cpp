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
#include <ctime>
#include <cstring>
#include <cstdlib>
#include <iostream>
#include <fstream>

#include "Launcher.hpp"
#include "Globals.hpp"
#include "easylogging++.h"
#include "IOHelper.hpp"
#include "GeometryHelper.hpp"

_INITIALIZE_EASYLOGGINGPP

using namespace launcher;

int main (int argc, char* argv[]) {
    
    if (argc != 17){
        std::cout << "wrong number of arguments (" << argc << "), requires exactly 17 | " << argv[3] << std::endl;
        exit(42);
    }
    
    
    //parse commandline arguments
    std::string workFolder(argv[1]);
    std::string typeString(argv[2]);
    int id = atoi(argv[3]);
    RAY_NUM = atoi(argv[4]);			//number of launched rays at the beginning
    MAX_ITERATIONS = atoi(argv[5]);			//maximum number of iteration = maximum number of events ray (useful to abort "ping-pong"-effect of a ray from one wall to an other)
    RECEIVE_THRESHOLD = atof(argv[6]);		//"size" of the antenna
    DIFFRACTION_THRESHOLD = atof(argv[7]);		//area around edge, in which diffraction events happen (suggested value: 7*lambda)
    REFLECTION_PART = atof(argv[8]);		//when a ray hits the wall this part of the energy (0..1) will contribute to the reflected ray
    WAVELENGTH = atof(argv[9]);			//wavelength is required for interference and diffraction
    INTERFERENCE = (atoi(argv[10])==1);		//let rays interfere instead of just adding the energies (= realistic small scale fading effects)
    MAX_RANGE = (atof(argv[11]));                   //maximum range of the antenna
    SAVERAYS = (atoi(argv[12])==1);                 //write rays to a file?
    DEBUG = (atoi(argv[13])>4);			//debugging information on numbers of rays and construction of the rayfile for the 3d viewer
    DEAD_DISTANCE = atof(argv[14]);			//after an event no new events happen for this long
    SCATTERING_PART = atof(argv[15]);		//this part of the energy (0..1) will be scattered when a ray hits a wall
    TIMEOUT = atof(argv[16]);	
    
    double rt;
    Vector<double> transmitter = getTransmitter(workFolder, id, rt);
    
    srand(42);
    double rxmin = 0, rxmax = 0, rymin = 0, rymax = 0, rzmin = 0, rzmax = 0;
    double sx = 0, sy = 0, sz = 0;
    int type = 0;
    std::vector<Vector<double> > receivers;
    
    std::string buildingsPolygons = workFolder + "polygons/buildings.txt";
    std::string terrainPolygons   = workFolder + "polygons/terrain.txt";
    std::string buildingsEdges    = workFolder + "edges/buildings.txt";
    std::string terrainEdges      = workFolder + "edges/terrain.txt";
    std::string rayFolder         = workFolder + "rays/";
    std::string receiverFile      = workFolder + "receivers.cfg";
    std::string coverageFile      = workFolder + "coverage/" + transmitter.toString() + ".txt";
    std::string logFile           = workFolder + "logs/launcher.log";
    
    easyloggingpp::Configurations conf;
    conf.setAll(easyloggingpp::ConfigurationType::ToFile, "true");
    conf.setAll(easyloggingpp::ConfigurationType::ToStandardOutput, "false");
    conf.setAll(easyloggingpp::ConfigurationType::Filename, logFile);
    conf.setAll(easyloggingpp::ConfigurationType::Format, "%datetime %level " + transmitter.toString() + " %log");
    if(!DEBUG) conf.set(easyloggingpp::Level::Debug, easyloggingpp::ConfigurationType::Enabled, "false");
    conf.set(easyloggingpp::Level::Warning, easyloggingpp::ConfigurationType::ToStandardOutput, "true");
    conf.set(easyloggingpp::Level::Warning, easyloggingpp::ConfigurationType::Format, "%datetime %level " + transmitter.toString() + " %log [%func]");
    easyloggingpp::Loggers::reconfigureLogger("default", conf);
    easyloggingpp::Loggers::reconfigureAllLoggers(conf);
    
    
  
    LOG(INFO) << "Extracted Transmitter " << transmitter << " in " << rt << " seconds.";
    LOG(INFO) << "Parse simulation type: " << typeString;
    //get simulation type and coordinates
    int e = parseType(typeString, rxmin, rymin, rzmin, rxmax, rymax, rzmax, sx, sy, sz, type);
    if(e != 0){
        LOG(WARNING) << "Could not parse simulation type";
        exit(EXIT_FAILURE);
    }

    // Store receivers if Point or List
    if(type == POINT){
        receivers.push_back(Vector<double>(rxmin, rymin, rzmin));
    }

    if(type == LIST){
        
        receivers = parseReceiverListFile(receiverFile);
    }

    if(type == LINE){
        receivers = parseReceiverLineFile(receiverFile);
    }

    
    LOG(DEBUG) << workFolder; 
    LOG(DEBUG) << buildingsPolygons;
    LOG(DEBUG) << buildingsEdges;
    LOG(DEBUG) << terrainPolygons;
    LOG(DEBUG) << terrainEdges;    
    LOG(DEBUG) << receiverFile;
    LOG(DEBUG) << coverageFile;
    LOG(DEBUG) << "parseTypeResult: " << type << " " << rxmin << " " << rymin << " " << rzmin << " " << rxmax << " " << rymax << " " << rzmax << " " << sx << " " << sy << " " << sz;
    LOG(DEBUG) << "Setpsizes: " << sx << " " << sy << " " << sz;
    
    std::time_t starttime, currenttime, totaltime;
    double runtime = 0.f;
    std::time(&totaltime);

    //load polygons and edges
    std::vector<std::vector<double> > polygons =parseFile(buildingsPolygons);
    std::vector<std::vector<double> > polygons2 =parseFile(terrainPolygons);
    for (int i=0; i < polygons2.size(); i++) {
        polygons.push_back(polygons2[i]);
    }
    
    std::vector<std::vector<double> > edges, edges2;
    edges  = parseFile(buildingsEdges);
    edges2 = parseFile(terrainEdges);   
    
    for (int i=0; i < edges2.size(); i++) {
        edges.push_back(edges2[i]);
    }

    if(MAX_RANGE > 0) {

        std::time(&starttime);
        LOG(INFO) << "Reducing Map Sizes to: " << MAX_RANGE;
        std::vector<std::vector<double> > polygonsLess;

        for(int j=0; j<polygons.size(); j++){
            std::vector<double> poly = polygons[j];

            for (int i = 0; i < poly.size() / 3; i++) {
                Vector<double> v(poly[i], poly[i + 1], poly[i + 2]);
                if (transmitter.distance(v) < MAX_RANGE) {
                    polygonsLess.push_back(poly);
                    break;
                }
            }
        }
        std::time(&currenttime);
        LOG(INFO) << "Polygons in smaller Map: " << polygonsLess.size();
        LOG(INFO) << "Needed time: " << std::difftime(currenttime, starttime);
        starttime = currenttime;
        polygons = polygonsLess;
    }

    //launch intial rays
    std::vector<Ray> rays;
    launch_rays(&rays, transmitter, 1.0, false, Vector<double>(0,0,0), false, Vector<double>(0,0,0),0,0,-1,RAY_NUM);
    bool done = true;

    std::time(&currenttime);
    LOG(INFO) << "Time launch_rays: " << std::difftime(currenttime, starttime);
    runtime += std::difftime(currenttime, starttime);
    starttime = currenttime;

    int iteration=0;
    std::time_t sttime, ctime = 0;
    for (iteration=0; iteration < MAX_ITERATIONS; iteration++) {
        done = true;

        std::time(&sttime)
;        LOG(DEBUG) << "iteration:" << iteration << "  #rays:" << rays.size();
        
        std::vector<Ray> newrays;
        for (int rayi = 0; rayi < rays.size(); rayi++) {
            if (rayi > 1000000000) exit(-42);
            std::time(&currenttime);
            if (TIMEOUT != 0 && difftime(currenttime, starttime) > TIMEOUT) {
                LOG(INFO) << "TIMEOUT!";
                break;
            }
            Ray *ray = &rays[rayi];
            if (ray->status == ACTIVE) {
                done = false;
                int eventtype = NOTHING;
                double eventdistance = 1000000;
                Vector<double> eventnormal;
                Vector<double> eventnormal2;
                Vector<double> eventconnection;
                Vector<double> eventedge;
                double eventslitwidth;

                // second check: ray reflected?
                for (int polyi=0; polyi<polygons.size(); polyi++) {

                    std::vector<double> poly = polygons[polyi];
                    Vector<double> location;
                    Vector<double> normal;
                    int tmp = getIntersection(ray->origin, ray->direction, poly, location, normal);
                    if (tmp > 0) {

                        double dst = (ray->origin - location).length();

                        if (normal * ray->direction > 0) { //avoid indoor reflections
                        //	normal*=-1; //make sure, normal points in right direction
                        //}
                            if (dst < eventdistance /*and dst > DEAD_DISTANCE*/) {

                                eventtype = REFLECTION;
                                eventdistance = dst;
                                eventnormal = normal;
                            }
                        }
                    }
                }

                // third check: ray diffracted?
                for (int edgei=0; edgei<edges.size(); edgei++) {
                    std::vector<double> edge = edges[edgei];
                    checkDiffraction(*ray,eventtype,eventdistance,eventconnection,eventedge,eventnormal, eventnormal2,eventslitwidth,edge,WAVELENGTH,DIFFRACTION_THRESHOLD, DEAD_DISTANCE);

                }




                switch (eventtype) {

                    case REFLECTION:
                        if (SCATTERING_PART > 0 || REFLECTION_PART > 0) {
                            double r = ((double)rand())/((double)RAND_MAX);

                            //the ray is always either reflected or diffracted in order to avoid a reduction of the sample size
                            //absorption & transmission loss is instead modeled by means of an energy reduction
                            double srthreshold = SCATTERING_PART / (SCATTERING_PART + REFLECTION_PART);
                            double energy = (REFLECTION_PART + SCATTERING_PART) * ray->energy;
                            if (r < srthreshold) {
                                doScattering(	&newrays,
                                                ray->origin + ray->direction * eventdistance,
                                                energy,
                                                eventnormal,
                                                ray->totalDistance + eventdistance,
                                                ray->numReflections + 1,
                                                rayi);
                            } else {
                                Vector<double> newdirection = ray->direction - (eventnormal * 2 * (ray->direction * eventnormal));
                                newdirection /= newdirection.length();
                                Vector<double> neworigin = ray->origin + ray->direction * eventdistance;
                                Ray newray(	neworigin[0],neworigin[1],neworigin[2],
                                                newdirection[0],newdirection[1],newdirection[2],
                                                energy,
                                                ACTIVE,
                                                ray->totalDistance + eventdistance,
                                                ray->numReflections + 1,
                                                rayi);
                                newrays.push_back(newray);
                            }
                        }
                        ray->status = SUCCEEDED;
                        ray->direction = ray->direction * eventdistance;
                    break;

                    case DIFFRACTION: 
                        doDiffraction(eventconnection, eventedge, eventslitwidth, eventdistance, eventnormal, eventnormal2, *ray, RAY_NUM_DIFFRACTION, newrays, rayi);
                        //newrays[newrays.size()-1].print();
                        ray->status = SUCCEEDED;
                        ray->direction = ray->direction * eventdistance;
                    break;

                    case NOTHING :
                        ray->status = ABORTED;
                }
            }
        }
        for (int rayi = 0; rayi < newrays.size(); rayi++) {
            if (rayi > 1000000000) exit(-42);
            Ray newray = newrays[rayi];
            rays.push_back(newray);
        }
        if (done) break;

        std::time(&ctime);
        LOG(DEBUG) << "Runtime: " << std::difftime(ctime, sttime) << "  #NewRays: " << newrays.size();
    }

    std::time(&currenttime);
    LOG(INFO) << "Total-Number of rays: " << rays.size();
    LOG(INFO) << "Needed time: " << std::difftime(currenttime, starttime);
    runtime += std::difftime(currenttime, starttime);
    starttime = currenttime;

    LOG(INFO) << "Total runtime (ray-launching): " << runtime;
    LOG(INFO) << "Calculating signal strength";
    
    std::stringstream res;
    res << std::scientific;
    //res << typeString << std::endl;
   
    
    //do for every receiver:
    if( type == POINT || type == LIST || type == LINE){        
        for(int ri = 0; ri < receivers.size(); ri++){
            Vector<double> point = receivers[ri];
            double energy = getEnergy(point, rays, transmitter);
            res << energy << " ";
        }
        res << std::endl;
    }
    
    else if( type == AREA ){
        double rz = rzmin;
        for (double ry = rymin; ry <= rymax; ry+=sy) {
            for (double rx = rxmin; rx <= rxmax; rx+=sx) {
                double energy = getEnergy(Vector<double>(rx,ry,rz), rays, transmitter);
                res << energy << " ";
            }
            res << std::endl;
        }
    }
    
    else if( type == CUBIG){
        for (double rz = rzmin; rz <= rzmax; rz+=sz) {
            for (double ry = rymin; ry <= rymax; ry+=sy) {
                for (double rx = rxmin; rx <= rxmax; rx+=sx) {
                    double energy = getEnergy(Vector<double>(rx,ry,rz), rays, transmitter);
                    res << energy << " ";
                    
                }
                res << std::endl;
            }
        }
    }

    std::ofstream myfile;
    myfile.open (coverageFile.c_str(), std::ios::out | std::ios::trunc);
    myfile << res.str();
    myfile.close();


    std::time(&currenttime);
    runtime = std::difftime(currenttime,starttime);
    LOG(INFO) << "Runtime for signalcalculation: " << runtime;
    
    runtime = std::difftime(currenttime,totaltime);
    LOG(INFO) << "total runtime: " << runtime;
        //LOG(DEBUG) << "link strength: " << 10.0*log10(energy) << "dB";



    /*
    if (!INTERFERENCE) {
        LOG(INFO) << "iterations: " << iteration;
        LOG(INFO) << "received energy: " << energy;
    } else {
        double energy_interfere = sqrt(received_field_im * received_field_im + received_field_re * received_field_re); 
        LOG(INFO) << "received energy: " << energy_interfere;
    } */
    if(SAVERAYS) {
        save_rays(rays, rayFolder, transmitter);
    }

    return 0;
}

