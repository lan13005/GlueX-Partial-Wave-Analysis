import os
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

fitName="EtaPi_fit" # location of the folder containing the inputs that were created from divideData.pl
seedFile="param_init.cfg" # seedFile name. Should also match the variable from divideData.pl 
seedAmpInit=9183 # choose a seed to randomly start to sample from
rndSamp_flag=True; # doesnt do anything right now
verbose=False
keepLogs=True

start = time.time()
workingDir = os.getcwd()
print("\n")
print("current working directory: %s" % (workingDir))
fitDir = workingDir+"/"+fitName
print("fit directory: %s" % (fitDir))

def getAmplitudesInBin(params):
    binNum,j=params
    os.chdir("bin_"+str(binNum))

    binCfgSrc = "bin_"+str(binNum)+"-full.cfg"
    binCfgDest, pols=writeCfg(lmes,binCfgSrc,seedAmpInit,j)
    
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
            status="C"
        elif "STATUS=FAILED" in output:
            status="F"
        elif "STATUS=CALL LIMIT" in output:
            status="L"
        else:
            status="U"
        print("Status: "+status)

        resultsFilePath=logDir+"_"+waveset+"/"+resultsFile
        print("Moving fit results to: "+os.getcwd()+resultsFilePath)
        if os.path.exists(resultsFile) and os.stat(resultsFile).st_size!=0: # if the fit files is not empty then we will try and use it
            shutil.move(resultsFile,resultsFilePath)
            getAmplitudeCmd='getAmpsInBin "'+binCfgDest+'" "'+resultsFilePath+'" "'+pols+'" "'+str(j)+'"'
            print(getAmplitudeCmd)
            getAmplitudeCmd=getAmplitudeCmd.split(" ")
            getAmplitudeCmd=[cmd.replace('"','') for cmd in getAmplitudeCmd]
            output=subprocess.check_output(getAmplitudeCmd)
            output=output.split("\n")
            for out in output:
                if len(out.split("\t"))>1:
                    if haveHeader==False and not out[0].isdigit():
                        outFile.write("status\t")
                        outFile.write(out+"\n")
                        haveHeader=True
                    if out[0].isdigit():
                        outFile.write(status+"\t")
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
    try:
        os.system("mkdir -p "+workingDir+"/"+"finalAmps/"+waveset)
    except:
        shutil.rmtree(workingDir+"/"+"finalAmps/"+waveset)
        os.system("mkdir -p "+workingDir+"/"+"finalAmps/"+waveset)
    for binNum in range(startBin,endBin):
        os.chdir("bin_"+str(binNum))
        files=[]
        for afile in os.listdir(logDir+"_"+waveset):
            fileTag=afile.split(".")[0]
            if "amplitude" in fileTag:
                if "Fit" not in fileTag:
                   files.append(logDir+"_"+waveset+"/"+afile) 
                   print(logDir+"_"+waveset+"/"+afile)
        if len(files)>0:
            os.system("cat "+files[0]+" > amplitudes.txt")
        if len(files)>1:
            os.system("tail -q -n 1 "+" ".join(files[1:])+" >> amplitudes.txt")
        os.system("cp amplitudes.txt "+workingDir+"/finalAmps/"+waveset+"/amplitudes-binNum"+str(binNum)+".txt")
        os.chdir("..")

### CHOOSE BIN NUMBER
if __name__ == '__main__':
    os.chdir(fitDir)
    startBin=0
    endBin=1
    numIters=1 # number of iterations to randomly sample and try to fit. No guarantees any of them will converge
    # EACH BIN SHARES THE SAME SEED FOR A GIVEN ITERATION
    seeds=[random.randint(1,100000) for _ in range(numIters)]
    processes=1 # number of process to spawn to do the fits
    if processes > (endBin-startBin)*numIters:
        print("You are trying to spawn more processes than available jobs")
        print(" choose better")
        exit();
    logDir="logs"

    #######################
    # Define the set of wavesets you want to loop over
    #######################
    lmess=[
            [
            [0,0,"+",True],
            [0,0,"-",True],
            [1,0,"+",False],
            [1,0,"-",False],
            [1,1,"+",False],
            [1,1,"-",False],
            [2,-1,"-",False],
            [2,0,"+",False],
            [2,0,"-",False],
            [2,1,"+",False],
            [2,1,"-",False],
            [2,2,"+",False]
            ],
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

    for lmes in lmess:
        waveset=constructOutputFileName(lmes)#.split("(")[0]
        cleanLogFolders()
        params=[(i,j) for i in range(startBin,endBin) for j in range(numIters)]
        p=Pool(processes)
        p.map(getAmplitudesInBin, params)
        p.terminate()
        gatherResults()
    
stop = time.time()
print("Execution time in seconds: %s" % (stop-start))
