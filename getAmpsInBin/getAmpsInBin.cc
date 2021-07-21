#include <iostream>
#include <set>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <string>
#include <vector>
#include <cassert>
#include <cstdlib>
#include <unistd.h>

// you need to modify this to your amptools location
#include "IUAmpTools/FitResults.h"

using namespace std;

int main( int argc, char* argv[] ){
    if (argc!=5){
        cout << "Requires 3 arguments: " << endl;
        cout << "The original cfg file, just to get the waveset from" << endl;
        cout << "The fit file which should be output from the `fit` program" << endl;
        cout << "the iteration number (i.e. when you do multiple fits with different initialization conditions you dont want to overwrite things" << endl;
        exit(-1);
    }
    string cfgFile(argv[1]);
    string resultsFile(argv[2]);
    string polString(argv[3]);
    string iter(argv[4]);

    cout << "Reading " << resultsFile << endl;
    FitResults results( resultsFile.c_str() );
    string fitName="EtaPi0";

    // Create output file
    string outFile="amplitudes"+iter+".txt";
    bool doAcceptanceCorrection=true;

    // Parse the cfg file name to determine the waveset
    string delimiter = "_";
    vector<string> lmes;
    size_t pos = 0;
    std::string token;
    while ((pos = cfgFile.find(delimiter)) != std::string::npos) {
        token = cfgFile.substr(0, pos);
        lmes.push_back(token);
        cfgFile.erase(0, pos + delimiter.length());
    }
    lmes.push_back(cfgFile.substr(0,cfgFile.find("(")));

    // Parse the polarization string to determine polarizations to consider
    vector<string> polarizations;
    pos = 0;
    while ((pos = polString.find(delimiter)) != std::string::npos) {
        token = polString.substr(0, pos);
        polarizations.push_back(token);
        polString.erase(0, pos + delimiter.length());
    }
    polarizations.push_back(polString);

    // **** HEADER FOR THE INTENSITIES
    for (auto lme: lmes){
        cout << lme << "\t" << lme+"_err" << "\t"; 
    }
    cout << "all\tall_err\t";

    // **** HEADER FOR THE PHASES
    int nPhases=0;
    set<set<string>> usedPhases;
    for (auto lme_i: lmes){
        for (auto lme_j: lmes){
                string sign_i = string{lme_i.back()};
                string sign_j = string{lme_j.back()};
                if ((sign_i != sign_j) || lme_i==lme_j)
                    continue;
                set<string> pairWaves;
                pairWaves.insert(lme_i);
                pairWaves.insert(lme_j);
                if (usedPhases.find(pairWaves) == usedPhases.end()){
                    cout << "phase"+lme_i+lme_j+"\tphase"+lme_i+lme_j+"_err\t"; 
                    ++nPhases;
                    usedPhases.insert(pairWaves);
                }
        }
    }

    // **** HEADER FOR THE REAL / IMAG PARTS OF THE AMPLITUDES
    for (auto lme: lmes)
        cout << "Re"+lme << "\t" << "Im"+lme << "\t"; 
    


    // **** EXTRA HEADER STUFF
    cout << "likelihood\titeration" << endl;
    
    //string polarizations[5]={"000","045","090","135","AMO"};
    //string polarizations[1]={"000"};
    
    //////////////////////////////////////////////////////////////
    ///////////////////     GET INTENSITIES   ////////////////////
    //////////////////////////////////////////////////////////////
    vector<string> all={};
    map<string,string> mapSignToRef{ {"+","Positive"},{"-","Negative"} };
    for (auto lme: lmes){
        string sign=string{lme.back()};
        string refl=mapSignToRef[sign];
        vector<string> etaPiAmp;
        for (auto polarization : polarizations){
            etaPiAmp.push_back((fitName+"_"+polarization+"::"+refl+"Im::"+lme).c_str());
            etaPiAmp.push_back((fitName+"_"+polarization+"::"+refl+"Re::"+lme).c_str());
            all.push_back((fitName+"_"+polarization+"::"+refl+"Im::"+lme).c_str());
            all.push_back((fitName+"_"+polarization+"::"+refl+"Re::"+lme).c_str());
        }
        pair< double, double > etaPiInt = results.intensity( etaPiAmp,doAcceptanceCorrection );
        cout << etaPiInt.first << "\t" << etaPiInt.second << "\t";
    }
    pair< double, double > allInt = results.intensity( all,doAcceptanceCorrection );
    cout << allInt.first << "\t" << allInt.second << "\t" ;

    //////////////////////////////////////////////////////////////
    //////////////////////////////////////////////////////////////
    //////////////////////////////////////////////////////////////

    
    //////////////////////////////////////////////////////////////
    ///////////////////     GET PHASE DIFFS   ////////////////////
    //////////////////////////////////////////////////////////////
    // This phase diff only makes sense between waves of a given sum. There are 4
    //   sums here: 2 from reflectivity and 2 from the Re and Im parts
    usedPhases.clear();
    for (auto lme_i: lmes){
        for (auto lme_j: lmes){
                string sign_i = string{lme_i.back()};
                string sign_j = string{lme_j.back()};
                string refl_i = mapSignToRef[sign_i];
                if ((sign_i != sign_j) || lme_i==lme_j)
                    continue;
                string tag = fitName+"_000::"+refl_i+"Im::";
                set<string> pairWaves;
                pairWaves.insert(lme_i);
                pairWaves.insert(lme_j);
                if (usedPhases.find(pairWaves) == usedPhases.end()){
                    pair< double, double > phase = results.phaseDiff( (tag+lme_i).c_str(), (tag+lme_j).c_str() );
                    cout << phase.first << "\t" << phase.second << "\t";
                    usedPhases.insert(pairWaves);
                }
        }
    }

    //////////////////////////////////////////////////////////////
    //////////////////////////////////////////////////////////////
    //////////////////////////////////////////////////////////////

    
    //////////////////////////////////////////////////////////////
    ///////////////////     GET REAL/IMAG PARTS   ////////////////////
    //////////////////////////////////////////////////////////////
    for (auto lme: lmes){
        string sign=string{lme.back()};
        string refl=mapSignToRef[sign];
        string ampName=fitName+"_000::"+refl+"Re::"+lme;
        cout << results.productionParameter(ampName).real() << "\t";
        cout << results.productionParameter(ampName).imag() << "\t";
    }
        
    //////////////////////////////////////////////////////////////
    //////////////////////////////////////////////////////////////
    //////////////////////////////////////////////////////////////
    cout << results.likelihood() << "\t" << iter << endl;


//    string newAmp="S0+";
//    vector<string> ampVec;
//    ampVec.push_back(newAmp);
//    map<string, complex<double>> prodParMap = results.ampProdParMap();
//    for (auto ele: prodParMap){
//        cout << ele.first << " " << ele.second << endl; 
//    }
    //cout << "complex " << newAmp << " = " << prodPar << endl; // " | intensity = " << results.intensity(ampVec).first << endl;


    chdir( ".." );
    
    return 0;
}
