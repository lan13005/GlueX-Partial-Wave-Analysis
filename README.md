divideData.pl will split the data into mass bins for all the input datasets

getAmpInBins folder needs to be put into your HALLD_SIM folder at $HALLD_SIM_HOME/src/programs/AmplitudeAnalysis/. In this AmplitudeAnalysis folder there should be a Sconscript file. Include the string "getAmpInBins" into the subdirs list. Modify getAmpsInBin/getAmpsInBin.cc to your waveset. Rebuild HALLD_SIM. 

runFits.py will run fits for a range of mass bins of your choice. It will use generate_cfg.py to generate configuration files for the specified wavesets. It will randomly initialize the waveset. 

After you run runFits.py a directory called finalAmps will be created. From here you can import the data (csv format) into your favorite plotting software and plot it. 
