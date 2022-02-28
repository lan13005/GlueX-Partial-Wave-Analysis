import os
import numpy as np
import subprocess

def checkLL():
    '''
    Do not care about fit status, only care that the likelihood is reasonable (negative and finite)
    '''
    searchStr="bestMinimum"
    if not os.path.exists(fitFileName):
        return False
    else:
        with open(fitFileName) as infile:
            for line in infile:
                if searchStr in line:
                    #searchStr=searchStr.rstrip().lstrip()
                    NLL=float(line.split(" ")[-1].split("\t")[1].rstrip().lstrip())
    return NLL<0 and np.isfinite(NLL)

def spawnProcessChangeSetting(old,new):
    '''
    Replace the value of varName to varValue in the file called fileName. Depending on the value type we can include quotes or not
    '''
    sedArgs=["sed","-i","s@"+old+"@"+new+"@g","setup_mass_dep_fits.py"]
    print(" ".join(sedArgs))
    subprocess.Popen(sedArgs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).wait()


fitFileName="etapi0_SD_TMD_piecewise_update.fit"

#ts=["010016", "016021", "021027", "027034", "034042", "042051", "051061", "061072", "072085", "085100","010016"]
ts=["010020","0200325","0325050","050075","075100","010020"]
for j in range(len(ts)-1):
    t=ts[j]
    os.system("mkdir -p overlayPlots")

    os.system("python setup_mass_dep_fits.py")
    
    if os.path.exists(fitFileName):
        print("Fit file already exists... Deleting it to reset fitting")
        os.system("rm "+fitFileName)
        os.system("rm fitAttempt*log")
    
    i=0
    while not checkLL():
        print("Starting a new fit attempt...")
        cmd="mpirun -np 9 fitMPI -c etapi0_SD_TMD_piecewise_EXAMPLE-copy.cfg -m 40000"
        pipeCmd=' > fitAttempt'+str(i)+'.log'
        os.system(cmd+pipeCmd)
        i+=1

#    # first argument (0,1,2) will run etapi_plotter, gather results, or do both
#    cmd="python3 overlayBins.py 2 'S0+-_S0++_D1--_D0+-_D1+-_D0++_D1++_D2++;S0+-;S0++;D1--;D0+-;D1+-;D0++;D1++;D2++;S0+-_S0++;D1--_D0+-_D1+-_D0++_D1++_D2++;D1--_D0+-_D1+-;D0++_D1++_D2++' 'etapi0_SD_TMD_piecewise_update.fit' '.'"
#    #cmd="python3 overlayBins.py 2 'S0+-_S0++_D0+-_D0++_D2+-_D2++;S0+-;S0++;D0+-;D0++;D2+-;D2++' 'etapi0_SD_TMD_piecewise_update.fit' '.'"
#    os.system(cmd)

    # Move results to the desired folder
    os.system("mkdir -p "+t)
    os.system("mv -f *.root "+t)
    os.system("mv -f etapi0_SD_TMD_piecewise_update.fit "+t)
    os.system("mv -f *.log "+t)
    os.system("mv -f *.ni "+t)
    os.system("mv -f overlayPlots "+t)
    spawnProcessChangeSetting(ts[j],ts[j+1])




