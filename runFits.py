import os
import numpy as np
import shutil
import math
import glob
import random
import sys
import subprocess
import time
import fileinput
from multiprocessing import Pool
from generate_cfg import writeCfg, constructOutputFileName
from determineAmbiguities import executeFinders

fitName="EtaPi_fit" # location of the folder containing the inputs that were created from divideData.pl
seedFileTag="param_init" # seedFile name. Should also match the variable from divideData.pl 
seedAmpInit=9183 # choose a seed to randomly start to sample from
rndSamp_flag=True; # doesnt do anything right now
verbose=False
keepLogs=True
doAccCorr="true" # has to be a string input

start = time.time()
workingDir = os.getcwd()
print("\n")
print("current working directory: %s" % (workingDir))
fitDir = workingDir+"/"+fitName
print("fit directory: %s" % (fitDir))

def getAmplitudesInBin(params):
    binNum,j=params
    seedFile=seedFileTag+"_"+str(j)+".cfg"
    os.chdir("bin_"+str(binNum))

    binCfgSrc = "bin_"+str(binNum)+"-full.cfg"
    binCfgDest, pols=writeCfg(lmes,binCfgSrc,seedAmpInit,j)
    os.system("touch "+seedFile)
    
    haveHeader=False
    with open(logDir+"_"+waveset+"/amplitude"+str(j)+".txt","w") as outFile, open(logDir+"_"+waveset+"/amplitudeFits"+str(j)+".log","w+") as logFile:
        callFit = "fit -c "+binCfgDest+" -s "+seedFile
        if verbose:
            print("First 5 current initial values for amplitudes:")
            print("----------------------------------")
            print("\n".join(subprocess.check_output(['grep','^initialize',binCfgDest]).split("\n")[:5]))
            print("----------------------------------")
            print("----------------------------------------------------------")
            print("Trying with seed="+str(seedAmpInit)+" at iteration="+str(j))
        print(("({0:.1f}s)(Bin {1})(Iteration {2}): "+callFit).format(time.time()-start,binNum,j))
    
        # We needed to create another fit results file so we can run things in parallel
        resultsFile="bin_"+str(binNum)+"-"+str(j)+".fit"
        if os.path.exists(resultsFile):
            os.remove(resultsFile)

        try:
            output=subprocess.check_output(callFit.split(" "))#, stdout=logFile, stderr=logFile)
        except subprocess.CalledProcessError as err:
            print("*** ABOVE CALL FAILED TO COMPLETE - TRY TO RUN THE FIT MANUALLY IN THE CORRESPONDING BIN FOLDER AS FOLLOWS ***\n*** cd {0}".format(fitDir+"/bin_"+str(binNum))+" ***\n*** "+callFit+" ***\n*** IF RUNFITS.PY DOES NOT EXIT BY ITSELF YOU SHOULD KILL IT MANUALLY NOW ***")
            exit(0)

        os.rename(binCfgDest,logDir+"_"+waveset+"/"+binCfgDest)

        logFile.write("ITERATION: "+str(j)+"\n")
        logFile.write(output)
        if "STATUS=CONVERGED" in output:
            status="C" # (C)onverged
        elif "STATUS=FAILED" in output:
            if "ERR MATRIX NOT POS-DEF" in [line.lstrip().rstrip() for line in output.split("\n")]:
                status="H" # (H)essian failed
            else:
                status="F" # (F)ailed 
        elif "STATUS=CALL LIMIT" in output:
            status="L" # (L)imit call 
        else:
            status="U" # (U)ncertain / unsure / unqualified
        print("Status: "+status)

        resultsFilePath=logDir+"_"+waveset+"/"+resultsFile
        print("Moving fit results to: "+os.getcwd()+"/"+resultsFilePath)
        if os.path.exists(resultsFile) and os.stat(resultsFile).st_size!=0: # if the fit files is not empty then we will try and use it
            shutil.move(resultsFile,resultsFilePath)
            if os.path.exists(seedFile) and os.stat(seedFile).st_size!=0: # param_init.cfg only exists if the fit converged
                shutil.move(seedFile,os.getcwd()+"/"+logDir+"_"+waveset+"/param_init_"+str(j)+".cfg")
            getAmplitudeCmd='getAmpsInBin "'+binCfgDest+'" "'+resultsFilePath+'" "'+pols+'" "'+str(j)+'" "'+doAccCorr+'"'
            print(getAmplitudeCmd)
            getAmplitudeCmd=getAmplitudeCmd.split(" ")
            getAmplitudeCmd=[cmd.replace('"','') for cmd in getAmplitudeCmd]
            output=subprocess.check_output(getAmplitudeCmd)
            output=output.split("\n")
            for out in output:
                if len(out.split("\t"))>1:
                    if haveHeader==False and out.split("\t")[-1]=="iteration": #not out[0].isdigit():
                        outFile.write("status\t")
                        outFile.write("solution\t") # In here solution is always O. When determining ambiguities solution would be like A1, A2 ... 
                        outFile.write(out+"\n")
                        haveHeader=True
                    if out[0].isdigit():
                        outFile.write(status+"\t")
                        outFile.write("O\t") 
                        outFile.write(out+"\n")
        else:
            print("fit file does not exist or is empty! The fit program failed to complete on bin {}".format(binNum))
            print("  fit file exists? {}".format(os.path.exists(resultsFile)))
            print("  fit file has non-zero size? {}".format(os.stat(resultsFile).st_size!=0))

    os.chdir("..")

def cleanLogFolders():
    '''
    Remove all the log/ directories in each bin folder
    '''
    print("Cleaning log folders")
    for binNum in range(startBin,endBin):
        os.chdir("bin_"+str(binNum))
        try:
            os.mkdir(logDir+"_"+waveset)
        except:
            shutil.rmtree(logDir+"_"+waveset)
            os.mkdir(logDir+"_"+waveset)
        os.chdir("..")

def gatherResults():
    '''
    Gather all the fit results into one file
    '''
    print("Grabbing all the results")
    for binNum in range(startBin,endBin):
        binName="bin_"+str(binNum)
        os.chdir(binName)
        files=[]
        listFiles=os.listdir(logDir+"_"+waveset)
        # sort the directories by length so names with "ambig" tags are last. They do not have a header for amplitude.txt
        listFiles=sorted(listFiles, key=lambda x: (len(x), x)) 
        for afile in listFiles:
            fileTag=afile.split(".")[0]
            if "amplitude" in fileTag:
                if "Fit" not in fileTag:
                   files.append(logDir+"_"+waveset+"/"+afile) 
                   print(binName+"/"+logDir+"_"+waveset+"/"+afile)
            if len(files)>0:
                os.system("cat "+files[0]+" > amplitudes.txt")
            if len(files)>1:
                os.system("tail -q -n 1 "+" ".join(files[1:])+" >> amplitudes.txt")
        os.system("cp amplitudes.txt "+workingDir+"/finalAmps/"+waveset+"/amplitudes-binNum"+str(binNum)+".txt")
        os.chdir("..")

def gatherMomentResults(verbose):
    '''
    Gather all the fit results into one file
    '''
    # Need to grab the mass binning to input to project_moments_polarized
    with open(workingDir+"/divideData.pl") as f:
        for line in f:
            if line.startswith("$lowMass"):
                lowMass=line.split("=")[-1].split(";")[0].rstrip().lstrip()
            if line.startswith("$highMass"):
                highMass=line.split("=")[-1].split(";")[0].rstrip().lstrip()
            if line.startswith("$nBins"):
                nBins=line.split("=")[-1].split(";")[0].rstrip().lstrip()
            if line.startswith("$fitName"):
                fitName=line.split("=")[-1].split(";")[0].rstrip().lstrip()
    print("Grabbing all the moments results")
    for binNum in range(startBin,endBin):
        outfile="moments-binNum"+str(binNum)+".txt"
        cmd="project_moments_polarized -o "+workingDir+"/finalAmps/"+waveset+"/"+outfile+" -w "+waveset+" -imax "+str(numIters)+" -b "+str(binNum)
        cmd+=" -mmin "+lowMass+" -mmax "+highMass+" -mbins "+nBins+" -fitdir "+fitName+" -v "+str(verbose)
        print("running: "+cmd)
        os.system(cmd)

### CHOOSE BIN NUMBER
if __name__ == '__main__':
    os.chdir(fitDir)
    startBin=0
    endBin=25
    numIters=50 # number of iterations to randomly sample and try to fit. No guarantees any of them will converge
    # EACH BIN SHARES THE SAME SEED FOR A GIVEN ITERATION
    seeds=[random.randint(1,100000) for _ in range(numIters)]
    processes=50 # number of process to spawn to do the fits
    if processes > (endBin-startBin)*numIters:
        print("You are trying to spawn more processes than available jobs")
        print(" choose better")
        exit();
    logDir="logs"

    #######################
    # Define the set of wavesets you want to loop over
    #######################
    lmess=[
            # S, D0, D1 + igore polarization / choose one reflectivity
#            [
#            [0,0,"+",True],
#            [2,0,"+",False],
#            [2,1,"+",False],
#            ],
#            [
#            [0,0,"+",True],
#            [2,-2,"+",False],
#            [2,-1,"+",False],
#            [2,0,"+",False],
#            [2,1,"+",False],
#            [2,2,"+",False],
#            ]
#            # S + TMD + P
#            [
#            [0,0,"+",True],
#            [0,0,"-",True],
#            [1,0,"+",False],
#            [1,0,"-",False],
#            [1,1,"+",False],
#            [1,1,"-",False],
#            [2,-1,"-",False],
#            [2,0,"+",False],
#            [2,0,"-",False],
#            [2,1,"+",False],
#            [2,1,"-",False],
#            [2,2,"+",False]
#            ],
#            # S + TMD 
#            [
#            [0,0,"+",True],
#            [0,0,"-",True],
#            [2,-1,"-",False],
#            [2,0,"+",False],
#            [2,0,"-",False],
#            [2,1,"+",False],
#            [2,1,"-",False],
#            [2,2,"+",False]
#            ],
#            # SPD positive M
#            [
#            [0,0,"+",True],
#            [0,0,"-",True],
#            [2,0,"-",False],
#            [2,0,"+",False],
#            [2,1,"-",False],
#            [2,1,"+",False],
#            [2,2,"-",False],
#            [2,2,"+",False],
#            [1,0,"+",False],
#            [1,0,"-",False],
#            [1,1,"+",False],
#            [1,1,"-",False]
#            ]
#            # SD positive M, epsilon
#            [
#            [0,0,"+",True],
#            [2,0,"+",False],
#            [2,1,"+",False],
#            [2,2,"+",False],
#            ]
#            # SD positive M, both refs
#            [
#            [0,0,"+",True],
#            [2,0,"+",False],
#            [2,1,"+",False],
#            [2,2,"+",False],
#            [0,0,"-",True],
#            [2,0,"-",False],
#            [2,1,"-",False],
#            [2,2,"-",False]
#            ]
# KMATRIX
            [
            [0,0,"+",True],
            [2,0,"+",False],
            [2,2,"+",False],
            [0,0,"-",True],
            [2,0,"-",False],
            [2,2,"-",False],
            ],
# ALL 
#            [
#            [0,0,"+",True],
#            [0,0,"-",True],
#            [2,-2,"-",False],
#            [2,-2,"+",False],
#            [2,-1,"-",False],
#            [2,-1,"+",False],
#            [2,0,"-",False],
#            [2,0,"+",False],
#            [2,1,"-",False],
#            [2,1,"+",False],
#            [2,2,"-",False],
#            [2,2,"+",False],
#            [1,-1,"+",False],
#            [1,-1,"-",False],
#            [1,0,"+",False],
#            [1,0,"-",False],
#            [1,1,"+",False],
#            [1,1,"-",False]
#            ]
    ]


    ######################
    # One day we can merge these sections but so far calculating ambiguites for {S,D0,D1} is implemented
    ######################
    for lmes in lmess:
        waveset=constructOutputFileName(lmes)#.split("(")[0]
        print(waveset)

        #### CODE TO DO RANDOMIZED FITS
        cleanLogFolders()
        params=[(i,j) for i in range(startBin,endBin) for j in range(numIters)]
        p=Pool(processes)
        p.map(getAmplitudesInBin, params)
        p.terminate()

        #### CODE TO EXTRACT THE AMBIGUITES
#    for lmes in lmess[:1]:
#        searchStrForAmps=["PositiveRe"] # Search strings that will be used to find amplitudes and ignore others, i.e. Since PositiveRe=PositiveIm we neglect Im part
#        searchStrForPols="000" # All the polarizations share the same amplitude so just pick one
#        binLocations=[fitDir+"/bin_"+str(binNum) for binNum in range(startBin,endBin)]
#        pols=["000","045","090","135","AMO"]
#        executeFinders(binLocations,numIters,processes,waveset,pols,searchStrForAmps,searchStrForPols,False) # Last argument is verbosity

    for lmes in lmess:
        #### GATHER RESULTS INTO FINALAMPS FOLDER
        waveset=constructOutputFileName(lmes)#.split("(")[0]
        try:
            os.system("mkdir -p "+workingDir+"/"+"finalAmps/"+waveset)
        except:
            shutil.rmtree(workingDir+"/"+"finalAmps/"+waveset)
        os.system("mkdir -p "+workingDir+"/"+"finalAmps/"+waveset)
        print(waveset)

        # Gather all the amplitudeFitsX.log files into a central location in the newly created directory 
        gatherResults()

        # Extract moments for all bins
        gatherMomentResults(0) # integer boolean argument is whether to verbose output
    
stop = time.time()
print("Execution time in seconds: %s" % (stop-start))
