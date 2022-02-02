/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
#include <iostream>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <string>
#include <vector>
#include <cassert>
#include <cstdlib>
#include <unistd.h>
#include <complex>
#include <string>
#include <time.h>

#include "IUAmpTools/FitResults.h"
#include "TFile.h"

#include "wave.h"
#include "moment.h"

#include "TFile.h"
#include <linux/limits.h>

std::string getcwd_string( void ) {
   char buff[PATH_MAX];
   getcwd( buff, PATH_MAX );
   std::string cwd( buff );
   cout << cwd << endl;
   return cwd;
}

int main( int argc, char* argv[] ){
    // these params should probably come in on the command line
    double lowMass;// = 0.7;
    double highMass;// = 2.5;
    int kNumBins;// = 45 };
    string fitDir;//("EtaPi_fit");
    bool verbose;
                     
    // set default parameters
    string outfileName("");
    string inputwaveset("");
    int imax=0;
    string binNum("");
    
    // parse command line
    for (int i = 1; i < argc; i++){
        string arg(argv[i]);
        
        if (arg == "-o"){
            if ((i+1 == argc) || (argv[i+1][0] == '-')) arg = "-h";
            else  outfileName = argv[++i]; }
        if (arg == "-w"){
            if ((i+1 == argc) || (argv[i+1][0] == '-')) arg = "-h";
            else  inputwaveset = argv[++i]; }
        if (arg == "-imax"){
            if ((i+1 == argc) || (argv[i+1][0] == '-')) arg = "-h";
            else  imax = stoi(string(argv[++i])); }
        if (arg == "-b"){
            if ((i+1 == argc) || (argv[i+1][0] == '-')) arg = "-h";
            else  binNum = argv[++i]; }
        if (arg == "-mmin"){
            if ((i+1 == argc) || (argv[i+1][0] == '-')) arg = "-h";
            else  lowMass = stod(argv[++i]); }
        if (arg == "-mmax"){
            if ((i+1 == argc) || (argv[i+1][0] == '-')) arg = "-h";
            else  highMass = stod(argv[++i]); }
        if (arg == "-mbins"){
            if ((i+1 == argc) || (argv[i+1][0] == '-')) arg = "-h";
            else  kNumBins = stoi(argv[++i]); }
        if (arg == "-fitdir"){
            if ((i+1 == argc) || (argv[i+1][0] == '-')) arg = "-h";
            else  fitDir = argv[++i]; }
        if (arg == "-v"){
            if ((i+1 == argc) || (argv[i+1][0] == '-')) arg = "-h";
            else{  
                string tmp=argv[++i];
                if(tmp=="0")
                    verbose = false; 
                else
                    verbose = true;
            }
        }
        if (arg == "-h"){
            cout << endl << " Usage for: " << argv[0] << endl << endl;
            cout << "\t -o <file>\t Ouput text file" << endl;
            cout << "\t -w <string>\t underscore separated waveset, i.e. S0+_S0-_D1+" << endl;
            cout << "\t -imax <int>\t max iteration number, in case you run multiple fits" << endl;
            cout << "\t -b <int>\t bin number to load results in" << endl;
            cout << "\t -mmin <double>\t min mass to consider" << endl;
            cout << "\t -mmax <double>\t max mass to consider" << endl;
            cout << "\t -mbins <int>\t number of mass bins" << endl;
            cout << "\t -fitdir <string>\t fit directory" << endl;
            cout << "Resulting txt file would be the moments for each iteartion in a given bin" << endl;
            exit(1);}
    }
    
    if (outfileName.size() == 0){
        cout << "use -h for help" << endl;
        exit(1);
    }
    
    string copyWaveset=inputwaveset;
    map<string,int> mapWaveToL={ {"S",0}, {"P",1}, {"D", 2} };
    string delimiter = "_";
    vector<wave> negative;
    vector<wave> positive;
    size_t pos = 0;
    std::string token;
    int L;
    int M;
    while ((pos = copyWaveset.find(delimiter)) != std::string::npos) {
        token = copyWaveset.substr(0, pos);
        L = mapWaveToL[token.substr(0,1)];
        if (token.substr(1,2)=="-1")
            M=stoi(token.substr(1,2));
        else
            M=stoi(token.substr(1,1));
        if (token.substr(token.size()-1,1)=="+")
            positive.push_back(wave(token.c_str(),L,M));
        else if (token.substr(token.size()-1,1)=="-")
            negative.push_back(wave(token.c_str(),L,M));
        copyWaveset.erase(0, pos + delimiter.length());
    }
    string lastToken=copyWaveset;
    L = mapWaveToL[lastToken.substr(0,1)];
    if (lastToken.substr(1,2)=="-1")
        M=stoi(lastToken.substr(1,2));
    else
        M=stoi(lastToken.substr(1,1));
    if (lastToken.substr(lastToken.size()-1,1)=="+")
        positive.push_back(wave(lastToken.c_str(),L,M));
    else if (lastToken.substr(token.size()-1,1)=="-")
        negative.push_back(wave(lastToken.c_str(),L,M));

    if (verbose){
        cout << "Loaded positive reflectivity waveset:" << endl;
        for(auto posWave: positive)
            cout << posWave.getName() << ", ";
        cout << endl;
        cout << "Loaded negative reflectivity waveset:" << endl;
        for(auto negWave: negative)
            cout << negWave.getName() << ", ";
        cout << endl;
    }

   //! Set waveset, has to be same order as in fit.cfg!
  coherent_waves wsPos, wsNeg;
  wsPos.reflectivity = +1;
  wsPos.waves = positive;

  wsNeg.reflectivity = -1;
  wsNeg.waves = negative;

  waveset ws;
  ws.push_back(wsPos);
  ws.push_back(wsNeg);
  
  //take for index step size 4 as there are two of the same waves next to each other corresponding to diff. sums
  size_t lastIdx = 0;
  for (size_t i = 0; i < ws.size(); i++) //ws.size gives number of coherent sums (=2 in this case, negative, positive)
    for (size_t j = 0; j < ws[i].waves.size(); j++, lastIdx += 4)// ws[i].waves.size() gives number of waves in given sum, index is increased by two for next wave as each wave takes two index for real and imaginary components
      ws[i].waves[j].setIndex(lastIdx);
    

  //LMAX=2*l_max (l_max is highest wave)
  //We consider M values form 0 to L, as H(LM)=H(L-M) due to parity invariance
  size_t LMAX;    //highest wave
  Biggest_lm(ws, &LMAX);


    double step = ( highMass - lowMass ) / kNumBins;
    
    ofstream outfile;
    outfile.open( outfileName.c_str() );

    outfile <<"M iteration"; //First line contains names of variables, first two colomns correspond to M(invariant mass) and t

    for (int L = 0; L<= int(LMAX); L++) {// the rest of the colomn correspond to moments
      for (int M = 0; M<= L; M++) {
	outfile<<" "<<"H0_"<<L<<M<<" "<<"H0_"<<L<<M<<"uncert.";
	outfile<<" "<<"H1_"<<L<<M<<" "<<"H1_"<<L<<M<<"uncert.";
      }
    }
    outfile<<endl;

    // descend into the directory that contains the bins
    chdir( fitDir.c_str() );

    //cout << "moving to dir: bin_" << binNum << endl; 
    ostringstream dir;
    dir << "bin_" << binNum;
    chdir( dir.str().c_str() );
    //getcwd_string();

    //cout << "moving to dir: logs_" << inputwaveset << endl; 
    chdir( ("logs_"+inputwaveset).c_str() );
    //getcwd_string();

    //Looping through M_eta_pi and t bins
    //for( int i = 0; i < kNumBins;i++ ){
    for( int iteration = 0; iteration < imax; iteration++ ){
        string resultsFile;
        resultsFile="bin_"+binNum+"-"+to_string(iteration)+".fit";
        FitResults results(resultsFile);

        // ------------------------
        //Printing entire list of parameters to make sure we are using correct parameters in the calculation
        if (verbose){
            const vector<string>& y=results.parNameList();
            const string* x=&y[0];
            for(int q = 0; q < (int)y.size(); q+=4){
              cout<<" Parameter order in results "<<x[q]<<endl;
            }
            //Printing list of real components of parameters to make sure we are using correct parameters in the calculation
            size_t lastIdx1 = 0;
            for (size_t c = 0; c < ws.size(); c++) //ws.size gives number of coherent sums (=2 in this case, negative, positive)
              for (size_t l = 0; l < ws[c].waves.size(); l++, lastIdx1 += 4)
                cout<<" Parameter order you chose "<<x[lastIdx1]<<endl;
        }
        // ------------------------

	outfile << lowMass + step * stoi(binNum) + step / 2. << " ";
        outfile << iteration << " ";

	if( !results.valid() ){
	  for (int L = 0; L<= pow(LMAX,1); L++) {// calculating moments and writing to a file
	    for (int M = 0; M<= L; M++) {
	      outfile << 0<< " "<< 0 <<" ";
	    }}
	  outfile << endl;
	  continue;
        }

        // print out the bin center
        for (int L = 0; L<= pow(LMAX,1); L++) {// calculating moments and writing to a file
            for (int M = 0; M<= L; M++) {
                // if(L==0 && M==0 && i==44 && j==3)cout <<" H0_00=  "<< real(decomposeMoment(0, L, M, ws, results.parValueList()))<<" H1_00=  "<< real(decomposeMoment(1, L, M, ws, results.parValueList()))<<" H2_00=  "<< decomposeMoment(2, L, M, ws, results.parValueList())<<endl;
                if ((M==L)*(L==pow(LMAX,1))){
                    outfile << real(decomposeMoment(0, L, M, ws, results.parValueList()))<< " "<< 0 << " ";
                    outfile << real(decomposeMoment(1, L, M, ws, results.parValueList()))<< " "<< 0 ;
                }
                else {
                    outfile << real(decomposeMoment(0, L, M, ws, results.parValueList()))<< " "<< 0 <<" ";
                    outfile << real(decomposeMoment(1, L, M, ws, results.parValueList()))<< " "<< 0 <<" ";
                }
            }
        }
        outfile << endl;
    }
    return 0;
}
