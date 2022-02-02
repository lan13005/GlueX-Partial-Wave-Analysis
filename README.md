## Amplitude Analysis Implementation for EtaPi
GlueX uses a variety of programs to perform amplitude analyses. This repository contains a set of scripts that orchestrates an analysis for the photoproduction of etapi0. An additional program is required in halld_sim, getAmpInBins which will be used to grab intensities+errors of the partial waves and the phases between them. Simple multiprocessing is used to run parallel fits. Supporting scripts exist to help modify and construct configuration files allowing one to loop over potential wavesets. Fit results are aggregated and results are plotted interactively using Jupyter-notebook. 

## Details of important programs
divideData.pl will split the data into mass bins for all the input datasets

getAmpInBins folder needs to be put into your HALLD_SIM folder at $HALLD_SIM_HOME/src/programs/AmplitudeAnalysis/. In this AmplitudeAnalysis folder there should be a Sconscript file. Include the string "getAmpInBins" into the subdirs list. The waveset to extract the amplitudes in will be determined by the name of the config file which will ultimately be created by runFits.py (which implements a config generator). Rebuild HALLD_SIM. 

project_moments_polarized is modified from the standard halld_sim repo to be compatible with the fit routines used in this repo. It takes in arguments instead of requiring recompiling to set fit directories and wavesets. Waves should be ordered such that positive and negative reflectivities are separated and the order of the wave initialization should be the same in the standard implementation. Ambiguities can be identified by looking at the moments; mathematical ambiguities must have the same moments but can have different amplitdes. 

runFits.py will run fits for a range of mass bins of your choice. It will use generate_cfg.py to generate configuration files for the specified wavesets based on some configuartion file you give it. It will randomly initialize the waveset. You can create a list of wavesets so you can run multiple sets of fits with different wavesets.

After you run runFits.py a directory called finalAmps will be created. From here you can import the data (csv format) into your favorite plotting software and plot it. This is where we must part ways as plotting can be tedious to make general. A good starting place is to use python + pandas + matplotlib. 
