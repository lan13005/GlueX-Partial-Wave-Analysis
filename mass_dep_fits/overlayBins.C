double lowMass=0.7;
double uppMass=2.5;
int nBins=1;
double stepMass=(uppMass-lowMass)/nBins;
string fitName="EtaPi_fit";

char slowMass[5];
char suppMass[5];

vector<string> groups={"_S0+-_S0++_D1--_D0+-_D1+-_D0++_D1++_D2++","_S0+-","_S0++","_D1--","_D0+-","_D1+-","_D0++","_D1++","_D2++","_S0+-_S0++","_D1--_D0+-_D1+-_D0++_D1++_D2++","_D1--_D0+-_D1+-","_D0++_D1++_D2++"};
void overlaySingleBin(int iBin,int nBins, vector<string> names1D, vector<TCanvas*> allCanvases){
	TPaveText *pt = new TPaveText();
        double dLowMass=lowMass+iBin*stepMass;
        double dUppMass=lowMass+(iBin+1)*stepMass;
	sprintf(slowMass,"%.2lf",dLowMass);
	sprintf(suppMass,"%.2lf",dUppMass);
	pt->Clear();
   	pt->AddText(("BIN_"+to_string(iBin)+" or Mass from ["+slowMass+","+suppMass+"] GeV").c_str()); 

        gStyle->SetOptStat(kFALSE);

        string fitLoc = fitName+"/bin_";
        string binNum = to_string(iBin);
        //string folder = fitLoc+binNum;
        string folder = ".";
        cout << "Moved into " << folder << endl;

        TH1F *any1DHist_dat;
        TH1F *any1DHist_acc;
        TH1F *any1DHist_bkg;
        TH1F *any1DHist_sig;

        cout << "Defined some variables..." << endl;

        int igroup=1;
        float tot_acc_yield;
        for (auto group:groups){
	    string outputFile = "/etapi_plot"+group+".root";
            cout << "opening: " << folder+outputFile << endl;
            TFile* infile = TFile::Open((folder+outputFile).c_str());

            TCanvas* c2=new TCanvas("","",1400,900); // plot all variables on a canvas for a given waveset
            c2->Divide(3,3);
            for (int histIdx=0; histIdx<(int)names1D.size(); ++histIdx){
                infile->GetObject((names1D[histIdx]+"dat").c_str(),any1DHist_dat);
                infile->GetObject((names1D[histIdx]+"acc").c_str(),any1DHist_acc);

                if (infile->GetListOfKeys()->Contains((names1D[histIdx]+"bkg").c_str())){
                    cout << "Bkg file is included! Will add the distribution onto acc" << endl;
                    infile->GetObject((names1D[histIdx]+"bkg").c_str(),any1DHist_bkg);
    	    	    any1DHist_bkg->SetFillColorAlpha( kBlue-6,0.5);
    	    	    any1DHist_bkg->SetLineColor(0);
                    //any1DHist_acc->Add(any1DHist_bkg);
                }

                allCanvases[histIdx]->cd(igroup);
                any1DHist_sig=(TH1F*)any1DHist_dat->Clone("signal");
                any1DHist_sig->Add(any1DHist_bkg,-1);
                //any1DHist_sig->Scale(1/any1DHist_sig->Integral(), "width");
                any1DHist_sig->Draw();
                any1DHist_sig->SetTitle(group.c_str());
                any1DHist_sig->SetMinimum(0);
                allCanvases[histIdx]->Update();

    	    	any1DHist_acc->SetFillColorAlpha( kOrange,0.5);
    	    	any1DHist_acc->SetLineColor( 0);
                if (igroup==1)
                    tot_acc_yield=any1DHist_acc->Integral();
                any1DHist_acc->Scale(any1DHist_sig->Integral()/tot_acc_yield);
                any1DHist_acc->Draw("HIST SAME");
                cout << "creating" << endl;

                auto legend = new TLegend(0.75,0.75,1.0,0.9);
                legend->AddEntry(any1DHist_sig,"signal","l");
                legend->AddEntry(any1DHist_acc,"acc","f");
                //legend->AddEntry(any1DHist_bkg,"bkg","f");
                legend->Draw();

                if (igroup==1){
                    // draw a pavetext showing the mass range for only the first pad
	            pt->Draw();
                }
                c2->cd(histIdx+1);
                any1DHist_sig->Draw();
                any1DHist_acc->Draw("HIST SAME");
                c2->Print(("overlayPlots/diagnostic"+group+".pdf").c_str(),"pdf");
            }
            ++igroup;
        }
        // we could have put this into the above loop but then we would have to open the same root file a lot more times
        for (int histIdx=0; histIdx<(int)names1D.size(); ++histIdx){
            if (names1D[histIdx]=="Phi"){
                names1D[histIdx]="BigPhi";
            }
            if (iBin==(nBins-1)){
                allCanvases[histIdx]->Print(("overlayPlots/"+names1D[histIdx]+".pdf)").c_str(),"pdf");
                continue;
            }
            if (iBin==0){
                allCanvases[histIdx]->Print(("overlayPlots/"+names1D[histIdx]+".pdf(").c_str(),"pdf");
            }
            if (iBin==(nBins-1)){
                allCanvases[histIdx]->Print(("overlayPlots/"+names1D[histIdx]+".pdf)").c_str(),"pdf");
            }
            else{
                allCanvases[histIdx]->Print(("overlayPlots/"+names1D[histIdx]+".pdf").c_str(),"pdf");
            }
        }
}

void overlayBins(){
        int ngroups=(int)groups.size();
        int flooredRoot=(int)sqrt(ngroups);
        int nrows, ncols;
        if (flooredRoot*flooredRoot>ngroups){
            nrows=flooredRoot;
            ncols=flooredRoot;
        }
        else if (flooredRoot*(flooredRoot+1)>ngroups){
            nrows=flooredRoot;
            ncols=flooredRoot+1;
        }
        else {
            nrows=flooredRoot+1;
            ncols=flooredRoot+1;
        }
        cout << "Dividing pad to have ncols,nrows: " << ncols << ", " << nrows << endl;

        TCanvas* anyCanvas;
        vector<TCanvas*> allCanvases;
        std::vector<std::string> names1D = {"Metapi","Metapi_40MeVBin","cosTheta","Phi","phi","psi","t"};
        for (auto name: names1D){
            anyCanvas = new TCanvas(("c"+name).c_str(),"",1440,900);
            anyCanvas->Divide(ncols,nrows);
            allCanvases.push_back(anyCanvas);
        }
        cout << "Defined all the canvases" << endl;

	//for (int iBin=0; iBin<48;++iBin){
	for (int iBin=0; iBin<nBins;++iBin){
	    	overlaySingleBin(iBin,nBins,names1D,allCanvases);
	}
}
