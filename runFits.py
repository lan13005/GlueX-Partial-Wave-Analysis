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
random.seed(seedAmpInit)

def sampleUniform(source,seed):
    '''
    This function takes in a config file and resample uniformly samples in the ranges specified
    '''
    random.seed(seed)
    if verbose:
        print("Randomly sampling initialization paramters with seed: "+str(seed))
    # Write the output 
    sampMin=-100
    sampMax=100
    with open(source,"r") as src:
        lines=src.readlines();
    with open(source,"w") as src:
        for line in lines:
            if line[:10]=="initialize":
                fields=line.split(" ")
                fields[3]=str(random.uniform(sampMin,sampMax))
                if fields[4]!="0.0":
                    fields[4]=str(random.uniform(sampMin,sampMax))
                src.write(" ".join(fields).rstrip())
                src.write("\n")
            else:
                src.write(line.rstrip())
                src.write("\n")

def getAmplitudesInBin(params):
    binNum,j=params
    os.chdir("bin_"+str(binNum))

    binCfgSrc = "bin_"+str(binNum)+"-full.cfg"
    binCfgDest = logDir+"bin_"+str(binNum)+"-full-"+str(j)+".cfg"
    os.system("cp "+binCfgSrc+" "+binCfgDest)
    os.system("sed -i 's/fit bin_"+str(binNum)+"/fit bin_"+str(binNum)+"-"+str(j)+"/' "+binCfgDest)
    
    haveHeader=False
    with open(logDir+"amplitude"+str(j)+".txt","w") as outFile, open(logDir+"amplitudeFits"+str(j)+".log","w+") as logFile:
        sampleUniform(binCfgDest,seed=seeds[j])
        callFit = "fit -c "+binCfgDest+" -s "+seedFile
        if verbose:
            print("First 5 current initial values for amplitudes:")
            print("----------------------------------")
            print("\n".join(subprocess.check_output(['grep','^initialize',binCfgDest]).split("\n")[:5]))
            print("----------------------------------")
            print("----------------------------------------------------------")
            print("Trying with seed="+str(seedAmpInit)+" at iteration="+str(j))
        print(("({0:.1f}s)(Bin {1})(Iteration {2}): "+callFit).format(time.time()-start,binNum,j))
    
        resultsFile="bin_"+str(binNum)+"-"+str(j)+".fit"
        if os.path.exists(resultsFile):
            os.remove(resultsFile)

        output=subprocess.check_output(callFit.split(" "))#, stdout=logFile, stderr=logFile)
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

        resultsFile="bin_"+str(binNum)+"-"+str(j)+".fit"
        resultsFilePath=logDir+resultsFile
        if os.path.exists(resultsFile):# and os.stat(resultsFile).st_size==0: # if the fit files is not empty then we will try and use it
            shutil.move(resultsFile,resultsFilePath)
            getAmplitudeCmd="getAmpsInBin "+resultsFilePath+" "+str(j)
            output=os.popen(getAmplitudeCmd).read()
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
    os.chdir("..")

def cleanLogFolders():
    '''
    Remove all the log/ directories in each bin folder
    '''
    print("Cleaning log folders")
    for binNum in range(startBin,endBin):
        os.chdir("bin_"+str(binNum))
        try:
            os.mkdir(logDir)
        except:
            shutil.rmtree(logDir)
            os.mkdir(logDir)
        os.chdir("..")

def gatherResults():
    '''
    Gather all the fit results into one file
    '''
    print("Grabbing all the results")
    try:
        os.mkdir(workingDir+"/"+"finalAmps")
    except:
        shutil.rmtree(workingDir+"/"+"finalAmps")
        os.mkdir(workingDir+"/"+"finalAmps")
    for binNum in range(startBin,endBin):
        os.chdir("bin_"+str(binNum))
        files=[]
        for afile in os.listdir(logDir):
            fileTag=afile.split(".")[0]
            if "amplitude" in fileTag:
                if "Fit" not in fileTag:
                   files.append(logDir+afile) 
                   print(logDir+afile)
        if len(files)>0:
            os.system("cat "+files[0]+" > amplitudes.txt")
        if len(files)>1:
            os.system("tail -q -n 1 "+" ".join(files[1:])+" >> amplitudes.txt")
        os.system("cp amplitudes.txt "+workingDir+"/finalAmps/amplitudes-binNum"+str(binNum)+".txt")
        os.chdir("..")

### CHOOSE BIN NUMBER
if __name__ == '__main__':
    os.chdir(fitDir)
    startBin=0
    endBin=30
    numIters=50 # number of iterations to randomly sample and try to fit. No guarantees any of them will converge
    # EACH BIN SHARES THE SAME SEED FOR A GIVEN ITERATION
    seeds=[random.randint(1,100000) for _ in range(numIters)]
    processes=32 # number of process to spawn to do the fits
    logDir="logs/"

    cleanLogFolders()
    params=[(i,j) for i in range(startBin,endBin) for j in range(numIters)]
    p=Pool(processes)
    p.map(getAmplitudesInBin, params)
    p.terminate()
    gatherResults()

stop = time.time()
print("Execution time in seconds: %s" % (stop-start))
