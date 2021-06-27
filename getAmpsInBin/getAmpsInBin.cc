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

#include "IUAmpTools/FitResults.h"

using namespace std;

int main( int argc, char* argv[] ){
    // parse command line
    if (argc!=3){
        cout << "Requires 2 arguments: The fit file and the iteration number" << endl;
        exit(-1);
    }
    string resultsFile(argv[1]);
    cout << "Reading " << resultsFile << endl;
    string iter(argv[2]);
    
    FitResults results( resultsFile.c_str() );
    string fitName="EtaPi0";

    // Create output file
    string outFile="amplitudes"+iter+".txt";
    bool doAcceptanceCorrection=true;
    //ofstream outfile;
    //outfile.open(outFile);
    //
    //
    ///////////////// ONLY INPUT YOU NEED TO CHANGE  ///////////////
    // Determine the waveset
    // Simple looping over all possible combinations of amplitudes*ms*reflectivies. i.e. D2-- is a D wave with m projection 2- and reflectivity -
    // include a drop vector with ignores a specific wave. Sometimes this looping is very convienent but will include all combinations. If we do
    //          not want a specific wave we can ignore it here
    ///////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////
    vector<string> amplitudes={"S","D"};//,"P"};
    vector<vector<string>> ms={ {"0"},{"1-","0","1+","2+"} };//,{"0","1+"} };
    vector<string> reflectivities={"Positive","Negative"}; // positive and negative
    vector<string> signs={"+","-"}; // exactly the same as the above but just in the sign represenation... +/positive and -/negative
    set<string> drop={"D1-+","D2+-"};//"D2--"}; // of the form D2-- where M=-2 and final - is the reflectivity
    ///////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////

    // **** HEADER FOR THE INTENSITIES
    for (int i=0; i<(int)signs.size(); ++i){
        string ref=reflectivities[i];
        int iamp=0;
        for (auto amp: amplitudes){
            for (auto m: ms[iamp]){
                string wave=amp+m+signs[i];
                if (drop.find(wave)!=drop.end()){
                    continue;
                }
                cout << ref+amp+m << "\t" << ref+amp+m+"_err" << "\t"; 
            }
            ++iamp;
        }
        cout << ref+"all\t"+ref+"all_err\t";
    }
    cout << "all\tall_err\t";

    // **** HEADER FOR THE PHASES
    int nPhases=0;
    set<set<string>> usedPhases;
    for (int i=0; i<(int)signs.size(); ++i){
        for (int iamp=0; iamp<(int)amplitudes.size(); ++iamp){
            for (auto mi: ms[iamp]){
                for (int jamp=0; jamp<(int)amplitudes.size(); ++jamp){
                    for (auto mj: ms[jamp]){
                        string wave1=amplitudes[iamp]+mi+signs[i];
                        string wave2=amplitudes[jamp]+mj+signs[i];
                        if( (iamp==jamp)*(mi==mj) || drop.find(wave1)!=drop.end() || drop.find(wave2)!=drop.end() )
                            continue;
                        set<string> pairWaves;
                        pairWaves.insert(wave1);
                        pairWaves.insert(wave2);
                        if (usedPhases.find(pairWaves) == usedPhases.end()){
                            cout << "phase"+wave1+wave2+"\tphase"+wave1+wave2+"_err\t"; 
                            ++nPhases;
                            usedPhases.insert(pairWaves);
                        }
                    }
                }
            }
        }
    }

    // **** HEADER FOR THE REAL / IMAG PARTS OF THE AMPLITUDES
    for (int i=0; i<(int)signs.size(); ++i){
        string ref=reflectivities[i];
        int iamp=0;
        for (auto amp: amplitudes){
            for (auto m: ms[iamp]){
                string wave=amp+m+signs[i];
                if (drop.find(wave)!=drop.end()){
                    continue;
                }
                //string ampName=fitName+"_000::"+ref+"Re::"+amp+m+signs[i];
                string ampName=amp+m+signs[i];
                cout << "Re"+ampName << "\t" << "Im"+ampName << "\t"; 
            }
            ++iamp;
        }
    }


    // **** EXTRA HEADER STUFF
    cout << "likelihood\titeration" << endl;
    
    //string polarizations[5]={"000","045","090","135","AMO"};
    string polarizations[1]={"000"};
    
    //////////////////////////////////////////////////////////////
    ///////////////////     GET INTENSITIES   ////////////////////
    //////////////////////////////////////////////////////////////
    vector< vector<string> > all={{},{}};
    for (int i=0; i<(int)signs.size(); ++i){
        for (int iamp=0; iamp<(int)amplitudes.size(); ++iamp){
            for (auto m: ms[iamp]){
                string wave=amplitudes[iamp]+m+signs[i];
                if (drop.find(wave)!=drop.end()){
                    continue;
                }
                vector<string> etaPiAmp;
                for (auto polarization : polarizations){
                    etaPiAmp.push_back((fitName+"_"+polarization+"::"+reflectivities[i]+"Im::"+amplitudes[iamp]+m+signs[i]).c_str());
                    etaPiAmp.push_back((fitName+"_"+polarization+"::"+reflectivities[i]+"Re::"+amplitudes[iamp]+m+signs[i]).c_str());
                }
                pair< double, double > etaPiInt = results.intensity( etaPiAmp,doAcceptanceCorrection );
                cout << etaPiInt.first << "\t" << etaPiInt.second << "\t";
            }
        }
        for (int iamp=0; iamp<(int)amplitudes.size(); ++iamp){
            for (auto polarization : polarizations){
                for (auto m: ms[iamp]){
                    string wave=amplitudes[iamp]+m+signs[i];
                    if (drop.find(wave)!=drop.end()){
                        continue;
                    }
                    all[i].push_back( (fitName+"_"+polarization+"::"+reflectivities[i]+"Im::"+amplitudes[iamp]+m+signs[i]).c_str() );
                    all[i].push_back( (fitName+"_"+polarization+"::"+reflectivities[i]+"Re::"+amplitudes[iamp]+m+signs[i]).c_str() );
                }
            }
        }
        pair< double, double > allInt = results.intensity( all[i],doAcceptanceCorrection );
        cout << allInt.first << "\t" << allInt.second << "\t" ;
    }
    std::vector<string> total;
    for (auto vec : all){
        total.insert(total.end(),vec.begin(),vec.end());
    }
    pair< double, double > allInt = results.intensity( total,doAcceptanceCorrection );
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
    for (int i=0; i<(int)signs.size(); ++i){
        for (int iamp=0; iamp<(int)amplitudes.size(); ++iamp){
            for (auto mi: ms[iamp]){
                for (int jamp=0; jamp<(int)amplitudes.size(); ++jamp){
                    for (auto mj: ms[jamp]){
                        //for (auto polarization : polarizations){
                        string wave1=amplitudes[iamp]+mi+signs[i];
                        string wave2=amplitudes[jamp]+mj+signs[i];
                        if( (iamp==jamp)*(mi==mj) || drop.find(wave1)!=drop.end() || drop.find(wave2)!=drop.end() )
                            continue;
                        string tag = fitName+"_000::"+reflectivities[i]+"Im::";
                        set<string> pairWaves;
                        pairWaves.insert(wave1);
                        pairWaves.insert(wave2);
                        if (usedPhases.find(pairWaves) == usedPhases.end()){
                            pair< double, double > phase = results.phaseDiff( (tag+wave1).c_str(), (tag+wave2).c_str() );
                            cout << phase.first << "\t" << phase.second << "\t";
                            usedPhases.insert(pairWaves);
                        }
                    }
                }
            }
        }
    }

    //////////////////////////////////////////////////////////////
    //////////////////////////////////////////////////////////////
    //////////////////////////////////////////////////////////////

    
    //////////////////////////////////////////////////////////////
    ///////////////////     GET REAL/IMAG PARTS   ////////////////////
    //////////////////////////////////////////////////////////////
    for (int i=0; i<(int)signs.size(); ++i){
        string ref=reflectivities[i];
        int iamp=0;
        for (auto amp: amplitudes){
            for (auto m: ms[iamp]){
                string wave=amp+m+signs[i];
                if (drop.find(wave)!=drop.end()){
                    continue;
                }
                string ampName=fitName+"_000::"+ref+"Re::"+amp+m+signs[i];
                cout << results.productionParameter(ampName).real() << "\t";
                cout << results.productionParameter(ampName).imag() << "\t";
            }
            ++iamp;
        }
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
