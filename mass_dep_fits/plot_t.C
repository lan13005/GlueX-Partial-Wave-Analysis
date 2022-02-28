//int ntbins=10;
//vector<string> ts={"010016", "016021", "021027", "027034", "034042", "042051", "051061", "061072", "072085", "085100"};
int ntbins=5;
vector<string> ts={"010020", "0200325", "0325050", "050075", "075100"};

map<string,string> prettyWave={
    {"S0++","S_{0}^{+}"},
    {"D2-+","D_{-2}^{+}"},
    {"D1-+","D_{-1}^{+}"},
    {"D0++","D_{0}^{+}"},
    {"D1++","D_{1}^{+}"},
    {"D2++","D_{2}^{+}"},
    {"S0+-","S_{0}^{-}"},
    {"D2--","D_{-2}^{-}"},
    {"D1--","D_{-1}^{-}"},
    {"D0+-","D_{0}^{-}"},
    {"D1+-","D_{1}^{-}"},
    {"D2+-","D_{2}^{-}"},
};


void overlaySingleBin(vector<string> wavesets,string histName, TCanvas* anyCanvas,string fout,int color){
        cout << "Starting overlaySingleBin" << endl;
        gStyle->SetOptStat(kFALSE);

        TH1F *any1DHist_dat;
        TH1F *any1DHist_acc;
        TH1F *any1DHist_bkg;
        TH1F *any1DHist_sig;
        
        TLatex* text = new TLatex();
        text->SetTextColor(color);
        text->SetTextFont(43);
        text->SetTextSize(60);


        int iw=0;
        for (auto waveset:wavesets){
            int it=1;
            float maxYield;
            for (auto t:ts){
                string title;
                if (t=="0325050")
                    title=t.substr(0,4).insert(1,".")+"<t<"+t.substr(4,6).insert(1,".");
                else
                    title=t.substr(0,3).insert(1,".")+"<t<"+t.substr(3,6).insert(1,".");
	        string outputFile = "etapi_plot_"+waveset+".root";
                cout << "opening: " << t+"/"+outputFile << endl;
                TFile* infile = TFile::Open((t+"/"+outputFile).c_str());

                infile->GetObject((histName+"_40MeVBindat").c_str(),any1DHist_dat);
                infile->GetObject((histName+"acc").c_str(),any1DHist_acc);

                if (infile->GetListOfKeys()->Contains((histName+"bkg").c_str())){
                    cout << "Bkg file is included! Will add the distribution onto acc" << endl;
                    infile->GetObject((histName+"_40MeVBinbkg").c_str(),any1DHist_bkg);
    	            any1DHist_bkg->SetFillColorAlpha( kBlue-6,0.5);
    	            any1DHist_bkg->SetLineColor(0);
                }

                cout << "Dividing canvas" << endl;
                cout << iw*ntbins+it << endl;
                anyCanvas->cd(iw*ntbins+it);
                cout << " Divided!" << endl;
                any1DHist_sig=(TH1F*)any1DHist_dat->Clone("signal");
                any1DHist_sig->Add(any1DHist_bkg,-1);

                if ((it==1)*(iw==0))
                    maxYield=any1DHist_sig->GetMaximum();
                cout << maxYield << endl;
                any1DHist_sig->SetMaximum(maxYield*1.1);
                any1DHist_sig->GetYaxis()->SetTickLength(0);
                any1DHist_sig->GetXaxis()->SetTickLength(0);
                any1DHist_sig->GetYaxis()->SetLabelSize(0);
                any1DHist_sig->GetXaxis()->SetLabelSize(0);
                any1DHist_sig->GetYaxis()->SetTitleSize(0);
                any1DHist_sig->GetXaxis()->SetTitleSize(0);

                any1DHist_sig->SetTitle(title.c_str());
                any1DHist_sig->Draw();
                any1DHist_sig->SetMinimum(0);
                anyCanvas->Update();
                cout << "Finished drawing signal" << endl;

    	        any1DHist_acc->SetFillColorAlpha( color,0.6);
    	        any1DHist_acc->SetLineColor( 0);
                any1DHist_acc->Scale(any1DHist_sig->GetBinWidth(1)/any1DHist_acc->GetBinWidth(1));
                any1DHist_acc->Draw("HIST SAME");
                cout << "Finished drawing amp weighted acceptance mc" << endl;

                if (it==ts.size()) text->DrawLatexNDC(0.6,0.65,prettyWave[waveset].c_str());

                //auto legend = new TLegend(0.75,0.75,1.0,0.9);
                //legend->AddEntry(any1DHist_sig,"signal","l");
                //legend->AddEntry(any1DHist_acc,"acc","f");
                //legend->Draw();
                ++it;
            }
            ++iw;
        }
        anyCanvas->SaveAs(fout.c_str());
        cout << "Finished drawing canvas!" << endl;
}

void plot_t(){
    gStyle->SetTitleY(0.99);
    gStyle->SetTitleSize(0.2,"title");
    gStyle->SetPadBorderMode(0);
    gStyle->SetFrameBorderMode(0);
    gluex_style->SetPadBottomMargin(0.0);
    gluex_style->SetPadLeftMargin(0.0);
    gluex_style->SetPadTopMargin(0.0);
    gluex_style->SetPadRightMargin(0.0);
    gluex_style->SetPadGridX(0);
    gluex_style->SetPadGridY(0); 	

    TCanvas* anyCanvas=new TCanvas("c","",2304,1300);
    string histName = "Metapi";

    int nrows=4;
    int ncols=ntbins;
    cout << "Dividing pad to have ncols,nrows: " << ncols << ", " << nrows << endl;
    anyCanvas->Divide(ncols,nrows,0,0);
    vector<string> wavesets={"S0+-","D1--","D0+-","D1+-"};
    string fout="tdep_negref_5tbins.png";
    overlaySingleBin(wavesets,histName,anyCanvas,fout,kBlue-7);

    wavesets={"S0++","D0++","D1++","D2++"};
    fout="tdep_posref_5tbins.png";
    overlaySingleBin(wavesets,histName,anyCanvas,fout,kRed-3);
}














