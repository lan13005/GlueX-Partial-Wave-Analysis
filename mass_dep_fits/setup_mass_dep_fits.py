import subprocess
import os
import random


baseDir="/d/grid17/ln16/myDSelector/amptools/"

def replaceStr(search,replace,fileName):
    print("replace str: "+replace)
    sedArgs=["sed","-i",'s@'+search+'@'+replace+'@g',fileName]
    #print("replacing: "+search+" with "+replace)
    subprocess.Popen(sedArgs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).wait()

fileName=baseDir+"mass_dep_fits/etapi0_SD_TMD_piecewise_EXAMPLE.cfg"
#fileName=baseDir+"mass_dep_fits/etapi0_SD_TMD_piecewise_EXAMPLE_nonLoop.cfg"

filePrefix=fileName.split(".")[0]
fileAffix=fileName.split(".")[1]
newFileName=filePrefix+"-copy."+fileAffix
print("copying "+fileName+" to "+newFileName)
os.system("cp "+fileName+" "+newFileName)

#sb="1"
for pol in ["000","045","090","135"]:
#for pol in ["000":#,"045","090","135"]:
    baseLoc=baseDir+"zPhase1_t0103061_e79828890/baseFiles_v3/tbins5/010020/"
    #baseLoc=baseDir+"zKmatrix_v4/"

    search="DATAFILE_"+pol
    fileLoc="amptools_data_phase1_t010020_e8288_tot_a2_pVHpi0p_"+pol+".root"
    #fileLoc="amptools_kmatrix_t011_e8288_tot_newWeights_a2_"+pol+".root"
    replace=baseLoc+fileLoc
    replaceStr(search,replace,newFileName)

    search="BKGNDFILE_"+pol
    fileLoc="amptools_data_phase1_t010020_e8288_sb_a2_pVHpi0p_"+pol+".root"
    #fileLoc="amptools_kmatrix_t011_e8288_sb_newWeights_a2_"+pol+".root"
    replace=baseLoc+fileLoc
    replaceStr(search,replace,newFileName)

    search="ACCMCFILE_"+pol
    fileLoc="amptools_flat_phase1_t010020_e8288_sig_a2_pVHpi0p_"+pol+".root"
    #fileLoc="amptools_flat_2018_8_t011_e8288_sig_newWeights_a2_"+pol+".root"
    replace=baseLoc+fileLoc
    replaceStr(search,replace,newFileName)

    search="GENMCFILE_"+pol
    fileLoc="amptools_flat_gen_phase_1_t010020_e8288_tree_flat_a2_pol"+pol+".root"
    #fileLoc="amptools_flat_2018_8_gen_t011_"+pol+".root"
    replace=baseLoc+fileLoc
    replaceStr(search,replace,newFileName)
    
#waves=["S01-","S01+","S02-","S02+","D01-","D01+","D21-","D21+","P01-","P01+","P11-","P11+"] 
waves=[
        "D0+-", "D0++", "D1+-", "D1++", "D2++", "D1--",
        "pD0+-", "pD0++", "pD1+-", "pD1++", "pD2++", "pD1--",
        ] # TMD waveset
refs=["Negative","Positive"]
parts=["Re","Im"]

def reinitWave(wave,anchor):
    for j,ref in enumerate(refs): 
        for i,part in enumerate(parts):
            refpart=ref+part
            if i==0:
                rsample=random.uniform(-10,10)
                isample=random.uniform(-10,10)
            search="initialize LOOPREAC::"+refpart+"::"+wave
            if anchor:
                replace=search+" cartesian "+str(rsample)+" 0 real"
            else:
                replace=search+" cartesian "+str(rsample)+" "+str(isample)
            replaceStr(search+".*",replace,newFileName)

print("\n------------------------------------------------\n")
print("reintializing production amplitudes")
print("------------------------------------------------\n")
#reinitWave("S0++",True)
#reinitWave("S0+-",True)
for wave in waves:
    reinitWave(wave,False)

searchStr="parameter pcwsBin"
constrainedParMap={}
print("\n------------------------------------------------\n")
print("reintializing piecewise production parameters between [-100,100]")
print("------------------------------------------------\n")
with open(newFileName) as newFile:
    for line in newFile:
        if line.startswith(searchStr):
            line=line.rstrip()
            parType , parName, parVal = line.split(" ")
            sample=random.uniform(0,10)
            replaceStr(line,parType+" "+parName+" "+str(sample),newFileName)
             

            
