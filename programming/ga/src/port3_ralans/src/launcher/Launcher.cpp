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
#include "Launcher.hpp"

#include <fstream>
#include <cstdlib>
#include <sstream>
#include <iostream>
#include <ctime>
#include <unistd.h>
#include <limits.h>

#include "Globals.hpp"
#include "easylogging++.h"
#include "GeometryHelper.hpp"


namespace launcher{
    
std::vector<Vector<double> >parseReceiverListFile(const std::string &filename){
    std::time_t st, ct;
    double rt;
    std::time(&st);

    LOG(INFO) << "Read Receiverlistfile...";
    std::ifstream infile;
    infile.open(filename.c_str());
    if(infile.fail()){
        LOG(WARNING) << "Can't open " << filename;
        exit(1);
    }
    
    std::string temp;
    std::vector<Vector<double> > receivers;
    while(std::getline(infile, temp)){
        std::istringstream ss(temp);
        double x,y,z;
        ss >> x >> y >> z;
        receivers.push_back(Vector<double>(x,y,z));
    }
    std::time(&ct);
    rt = std::difftime(ct,st);
    LOG(INFO) << "Finished in " << rt << " seconds.";
    return receivers;
}
/**
* Parses file with space-seperated files into a 2d vector.
**/
    /**
std::vector<std::vector<double> > parseFile (std::string filename) {
	std::ifstream infile;
	infile.open (filename);
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
    */
void launch_rays(std::vector<Ray> * rays, Vector<double> origin, double total_energy, bool active1, Vector<double> normal1, bool active2, Vector<double> normal2, double totalDistance, int numReflections,int predecessor, int numRays) {
	int ray_num_theta=sqrt(1.0*numRays/2)*2;
	int ray_num_phi=sqrt(1.0*numRays/2);
	double dangle=PI/ray_num_phi;
	for (int thetai = 0; thetai < ray_num_theta; thetai++) {
		double theta = thetai * dangle;
		
		for (int phii = 0; phii < ray_num_phi; phii++) {
			double phi = phii * dangle;
			double dx = sin(theta) * cos(phi);
			double dy = sin(theta) * sin(phi);
			double dz = cos(theta);
			Vector<double> direction(dx,dy,dz);
			double energy =  total_energy / numRays;
			if(!active1 || (active1 && direction*normal1>0) || (active2 && direction*normal2>0) ) {
				Ray r (	origin[0], origin[1], origin[2],
					dx,dy,dz,
					energy,
					ACTIVE,
					totalDistance,
					numReflections,
					predecessor);
				rays -> push_back(r);
			}
		}
	}
}

/**
  * launches a scattered ray in a random direction
  **/
void doScattering(std::vector<Ray> * rays, Vector<double> origin, double energy, Vector<double> normal, double totalDistance, int numReflections, int predecessor) {
	bool launched = false;
	while(!launched) {
		double r = ((double)rand())/((double)RAND_MAX);
		double theta = r * 2.0 * PI;
		r = ((double)rand())/((double)RAND_MAX);
		double phi = r * PI;
		double dx = sin(theta) * cos(phi);
		double dy = sin(theta) * sin(phi);
		double dz = cos(theta);
		Vector<double> direction(dx,dy,dz);
		if (direction*normal < 0) {
			Ray r (	origin[0], origin[1], origin[2],
				dx,dy,dz,
				energy,
				ACTIVE,
				totalDistance,
				numReflections,
				predecessor);
			rays -> push_back(r);
			launched = true;
		}
	}
}


/**
 * Check if the given ray gets near to an edge. If yes, the event is updated.
 */
void checkDiffraction(Ray ray, int &eventtype, double &eventdistance, Vector<double> &eventconnection, Vector<double> &eventedge, Vector<double> &eventnormal1, Vector<double> &eventnormal2, double &eventslitwidth, std::vector<double> edge, double WAVELENGTH, double DIFFRACTION_THRESHOLD, double DEAD_DISTANCE) {
	Vector<double> e1(edge[0],edge[1],edge[2]);
	Vector<double> e2(edge[3],edge[4],edge[5]);
	Vector<double> n = (e2-e1).cross(ray.direction);
	if (n * n != 0) { //rays not parallel
		n.normalize();
		double dst2 = std::abs(e1 * n - ray.origin * n); //distance between lines from hesse normal form
		dst2 /= WAVELENGTH;
		if (dst2 < DIFFRACTION_THRESHOLD) {
			Vector<double> n2 = (e2-e1).cross(n);
			n2.normalize();
			double d = n2 * e1;
			double dst = ( d - ray.origin * n2) / (ray.direction * n2);
			if (dst > EPSILON) {
				n2 = ray.direction.cross(n);
				n2.normalize();
				d = n2 * ray.origin;
				double lambda = ( d - e1 * n2 ) / ( (e2-e1) * n2 );
				if (lambda > 0 && lambda < 1 && dst < eventdistance && dst > DEAD_DISTANCE) {
						eventtype = DIFFRACTION;
						eventdistance = dst;
						eventnormal1 = Vector<double>(edge[6],edge[7],edge[8]);
						eventnormal2 = Vector<double>(edge[9],edge[10],edge[11]);
						eventconnection = n;
						eventedge = (e2-e1) / (e2-e1).length();
						eventslitwidth = 6.0 * dst2;
				}
			}
		}
	}
}

/**
 * This is the diffraction calculation (as described in  "AN IMPROVED ENERGETIC APPROACH TO DIFFRACTION BASED ON THE UNCERTAINTY PRINCIPLE" from Stephenson, Uwe). New rays are launched, that are bend to the sides. The energy is distributed to them according to dapdf.
 */
void doDiffraction(Vector<double> eventconnection, Vector<double> eventedge, double eventslitwidth, double eventdistance, Vector<double> eventnormal1, Vector<double> eventnormal2, Ray ray, int NUMRAYS, std::vector<Ray> &newrays, int predecessor) {


	std::vector<Ray> locrays;
	double normalizer=0;
	//new rays are launched in a plane that contains the ray and is as near as possible to
	//a plane orthogonal to the edge.
	//Thus, it contains the shortest connection between ray and edge.
	Vector<double> rotaxe = eventconnection.cross(ray.direction);
	//the old and the new ray are projected onto a plane orthogonal to the edge because this is where the angle of diffractoon is determined
	//a local coordinate system in this plane is used for this
	Vector<double> loccsx = eventconnection/eventconnection.length();
	Vector<double> loccsy = loccsx.cross(eventedge);
        
        //REFACTORING: Converted Vector2d to Vector<double>
	Vector<double> oldrayproj(loccsx * ray.direction, loccsy * ray.direction, 0.);

	for (int i=0; i< NUMRAYS; i++) {
		double angle = -0.75 * PI +1.5*PI/(1.0*NUMRAYS)*i;
                
		Vector<double> newraydirection = ray.direction.rotate(rotaxe, angle);
		 
                //REFACTORING: Converted Vector2d to Vector<double>
		Vector<double> newrayproj(loccsx * newraydirection, loccsy * newraydirection, 0. );
		double a = getAngle(oldrayproj,newrayproj);
		//std::cout << "a " << a << " angle " << angle << std::endl;
		double val = dapdf(a, eventslitwidth);
		//if (!(newraydirection.dot(eventnormal1)>0 ||newraydirection.dot(eventnormal2)>0)) val=0;
		normalizer += val;
		Vector<double> origin = ray.origin + ray.direction * eventdistance;
		Ray r (	origin[0], origin[1], origin[2],
				newraydirection[0],newraydirection[1],newraydirection[2],
				val,
				ACTIVE,
				ray.totalDistance + eventdistance,
				ray.numReflections,
				predecessor);
		locrays.push_back(r);
		
	}
	double sum = 0;
	//rather hacky to reuse code from non-random version:
	double r = ((double)rand())/((double)RAND_MAX);
	for (int i=0; i < locrays.size(); i++) {
		sum += locrays[i].energy / normalizer;
		if (sum > r) {
			locrays[i].energy = ray.energy;
			newrays.push_back(locrays[i]);
			//std::cout << "pushing back" << std::endl;
			break;
		}
	}
	//std::cout << "r " << r << " sum " << sum << std::endl;
	//std::cout << "number of new rays: " << newrays.size() << std::endl;
}

std::string getIdentifier(const std::string &filename){
 
    /* remove directories*/
    size_t pos1, pos2;
    std::string temp;
        
    char hostname[HOST_NAME_MAX + 1];
    int e = gethostname(hostname,HOST_NAME_MAX + 1);
    
    pos1 = filename.find(hostname) + strlen(hostname) + 1;
    //pos2 = filename.find()
    temp = filename.substr(pos1, std::string::npos);
    //std::cout << temp << std::endl;
    //temp = filename.substr(temp.find_first_of("/"), std::string::npos);
    
    while( std::string::npos != (pos2 = temp.find_last_of("/")) ){
        temp = temp.substr(0, pos2);
        //std::cout << temp << std::endl;
    }
    
    return temp;
    
}

std::string getTmpFolder(const std::string &filename){
    
    size_t pos;
    pos = filename.find("tmp/") + 4;
    
    std::string temp = filename.substr(0, pos);
    return temp;
}

std::string getWorkFolder(const std::string &filename){
    
    char hostname[HOST_NAME_MAX + 1];
    int e = gethostname(hostname,HOST_NAME_MAX + 1);
    //std::cout << "Hostname: " << hostname << std::endl;
    std::string temp = getTmpFolder(filename);
    temp.append(hostname);
    temp += '/';
    //std::cout << "temo: " << temp << std::endl;
    temp += getIdentifier(filename) + "/";
    //std::cout << "wfolder " << temp << std::endl;
    return temp;
}

Vector<double> getTransmitter(const std::string &workfolder, const int &id, double &rt){
    std::time_t st, ct;
    std::time(&st);

    std::string filename(workfolder);
    filename += "transmitters.cfg";
    
    std::ifstream infile;
    infile.open(filename.c_str());
    if(infile.fail()){
        std::cout << "Can't open " << filename << std::endl;
        exit(1);
    }
    
    std::string temp;
    std::vector<Vector<double> > receivers;
    
    int i = 0;
    for(i=0; std::getline(infile, temp) && i < id; i++);
    
    if (i != id){
        std::cout << "Could not get requested Transmitter" << std::endl;
    }
    
    std::istringstream ss(temp);
    double x,y,z;
    ss >> x >> y >> z;
    
    
    std::time(&ct);
    rt = std::difftime(ct,st);
   
    return Vector<double>(x,y,z);
}

double getEnergy(const Vector<double> &receiver, const std::vector<Ray> &rays, const Vector<double> &tr){
    if(MAX_RANGE > 0 && MAX_RANGE < tr.distance(receiver)){
        //LOG(DEBUG) << MAX_RANGE << " | " << std::abs(tr.distance(receiver)) << " | " << tr << receiver;
        return 0;
    }

    //LOG(DEBUG) << "in getEnergy";
    //energy can be saved in a complex number in order to generate interference effects. Warning: the calculation is not physically correct, for this the field strengths instead of the energies would have to be used. Still, this calculation leads to the expected effect. (large & small scale fading)            
    double received_field_im = 0;
    double received_field_re = 0;

    //Instead, the energy can just be saved as a real number if no interference shall be calculated. (just large scale fading)
    double energy = 0;

    //these vectors need to be refilled for each receiver (TODO: use arrays for performance?)
    std::vector<int> flags;
    std::vector<double> distances;
    //first, we need to find out, what ray segments cross receivers
    for (int rayi = 0; rayi < rays.size(); rayi++) {
        if (rayi > 1000000000) exit(-42);
        const Ray *ray = &(rays[rayi]);
        int flag = UNKNOWN;
        double td = 0;
        if (ray->status != ACTIVE) { //These rays exist because of timeout or max_iterations. Maybe, they hit obstacles first, so it's better to ignore them.
            Vector<double> direction;
            direction = ray->direction;

            //the length of the ray shows, where it hits a wall or edge (if it's not an aborted one), we need this value
            double maxdst=direction.length();
            direction = direction / maxdst;

            double dst = direction * (receiver - ray->origin);		//distance the ray segment covered from its origin to the receiver
            if (dst > 0) {
                //double dst2 = (dst * direction - (receiver-ray->origin)).norm();
                double dst2 = (direction * dst - (receiver-ray->origin)).length();	//distance of the ray to the receiver
                if (dst2 < RECEIVE_THRESHOLD && (ray->status == ABORTED || dst < maxdst) ) {
                    //ray->direction = direction * dst; //TODO: only for debugging has to be removed, when several transmitters are used
                    //ray->status = MAYBE_RECEIVED; //TODO: only for debugging has to be removed, when several transmitters are used
                    flag = MAYBE_RECEIVED;
                    if(INTERFERENCE) {
                        if(ABORTED) {
                            td = ray->totalDistance + dst;
                        } else {
                            td = ray->totalDistance - maxdst +dst;
                        }
                    }
                }
            }
        }
        flags.push_back(flag);
        if (INTERFERENCE) {
            distances.push_back(td);
        }
    }


    //see if marked raysegments are the first received ones of a ray
    for (int rayi = 0; rayi < rays.size(); rayi++) {
        if (rayi > 1000000000) exit(-42);
        const Ray *ray = &(rays[rayi]);

        if (flags[rayi] == MAYBE_RECEIVED) {
            bool predecessorReceived = false;
            int id = ray->predecessor;
            while (id > -1) {
                if (flags[id] == MAYBE_RECEIVED || flags[id]==RECEIVED) {
                    predecessorReceived = true;
                    break;
                }
                id = rays[id].predecessor;
            }
            if (!predecessorReceived) {
                //ray->status = RECEIVED;//TODO: only for debugging has to be removed, when several transmitters are used
                flags[rayi] = RECEIVED;
                if (!INTERFERENCE) {
                    //real calculation (simple / just small scale fading)
                        energy += ray->energy;
                } else {
                    //complex calculation (for interference):
                    double field_value, field_angle, field_re,field_im;
                    field_value = ray->energy;
                    field_angle = fmod(distances[rayi], WAVELENGTH)/WAVELENGTH*2.0*PI; //current phase
                    field_angle *= pow(-1,ray->numReflections); //phase jumps generated by reflections
                    field_re = field_value * cos(field_angle);
                    field_im = field_value * sin(field_angle);
                    received_field_re += field_re;
                    received_field_im += field_im;
                }
            } 
        }

    }
    if (!INTERFERENCE) {
        //LOG(DEBUG) << energy;
        return energy;
    } else {
        double energy_interfere = sqrt(received_field_im * received_field_im + received_field_re * received_field_re); 
        //LOG(DEBUG) << energy_interfere;
        return energy_interfere;
    }
}

// Also working for more than one line
std::vector<Vector<double> > parseReceiverLineFile(const std::string &filename){
    std::ifstream infile;
    infile.open(filename.c_str());
    if(infile.fail()){
        LOG(WARNING) << "Can't open " << filename;
        exit(1);
    }
    
    std::string temp;
    std::vector<Vector<double> > receivers, receivers2, out;
    std::vector<double> steps;
    
    //read all lines
    while(std::getline(infile, temp)){
        std::istringstream ss(temp);
        //LOG(DEBUG) << ss.str();
        double xa, ya, za, xe, ye, ze, s;
        ss >> xa >> ya >> za >> xe >> ye >> ze >> s;
        receivers.push_back(Vector<double>(xa,ya,za));
        receivers2.push_back(Vector<double>(xe,ye,ze));
        steps.push_back(s);
    }
    
    //calculate every position
    for(int i = 0; i < 1/*steps.size()*/; i++){
        Vector<double> start = receivers[i];
        Vector<double> end = receivers2[i];
        double step = steps[i];
        Vector<double> vec = start - end;
        double leng = vec.length();
        vec.normalize();
        vec *= step;
        Vector<double> cur = start;
        
        while( (cur - start).length() <= leng){
            out.push_back(Vector<double>(cur));
            cur += vec;
        }
        
    }
    //LOG(DEBUG) << "Anzahl Elem " << out.size();
    return out;
    
}

int parseType(const std::string &type, double &xmin, double &ymin, double &zmin, double &xmax, double &ymax, double &zmax, double &sx, double &sy, double &sz, int &t){
    //LOG(DEBUG) << type;
    std::stringstream ss(type);
    ss >> t;
    //LOG(DEBUG) << "type: " << t;
    switch(t){
        case POINT:
            ss >> xmin >> ymin >> zmin;
            break;
        case LINE:
            break;
        case AREA:
            ss >> xmin >> ymin >> xmax >> ymax >> zmin >> sx >> sy;
            zmax = zmin;
            break;
        case CUBIG:
            ss >> xmin >> ymin >> zmin >> xmax >> ymax >> zmax >> sx >> sy >> sz;
            break;
        case LIST:
            break;
        default:
            //LOG(DEBUG) << "Unsupported type: " << t;
            return -1;
            break;
    }
    return 0; 
    
}

}
