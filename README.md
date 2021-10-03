divideData.pl will split the data into mass bins for all the input datasets

getAmpInBins folder needs to be put into your HALLD_SIM folder at $HALLD_SIM_HOME/src/programs/AmplitudeAnalysis/. In this AmplitudeAnalysis folder there should be a Sconscript file. Include the string "getAmpInBins" into the subdirs list. The waveset to extract the amplitudes in will be determined by the name of the config file which will ultimately be created by runFits.py (which implements a config generator). Rebuild HALLD_SIM. 

runFits.py will run fits for a range of mass bins of your choice. It will use generate_cfg.py to generate configuration files for the specified wavesets based on some configuartion file you give it. It will randomly initialize the waveset. You can create a list of wavesets so you can run multiple sets of fits with different wavesets.

After you run runFits.py a directory called finalAmps will be created. From here you can import the data (csv format) into your favorite plotting software and plot it. This is where we must part ways as plotting can be tedious to make general. A good starting place is to use python + pandas + matplotlib. 
