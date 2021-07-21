import random
import sys
import re
import os

'''
The goal of this code is to generate config files with any type of waveset
Part of the reference config file will be taken to form the preamble of the output
config file. This preamble will contain the dataset names, fit name, scales, etc

For each wave we want to include we need to do the following
    1. Initialize the wave
    2. Constrain the wave
    3. Scale the waves
'''

def constructWave(l,m,e):
    '''
    constructs the wave in the typical notation
    '''
    mapSpinToSpectroscopic={0:"S",1:"P",2:"D"}
    waveString=mapSpinToSpectroscopic[l]+str(m)
    if e=="+":
        waveString+="+"
    else:
        waveString+="-"
    return waveString

def constructWaveString(l,m,e,c,prefix):
    '''
    l = Spin {0, 1, 2 ...}
    m = Spin projection {..., -2, -1, 0, 1+, 2+, ... }
    e = reflectivity {+/-}
    c = component (Re)al or (Im)aginary part
    prefix = string containing the dataset name
    '''
    assert l <= 2 and l >= 0  # Just do up to D waves for now
    assert abs(m) <= l
    assert e in ["+","-"]

    waveString=prefix+"::"
    if e=="+":
        waveString+="Positive"
    else:
        waveString+="Negative"
    waveString+=c+"::"
    waveString+=constructWave(l,m,e)
    return waveString
    
def defineWave(l,m,e):
    '''
    l = Spin {0, 1, 2 ...}
    m = Spin projection {..., -2, -1, 0, 1+, 2+, ... }
    e = reflectivity {+/-}
    '''
    assert l <= 2 and l >= 0  # Just do up to D waves for now
    assert abs(m) <= l
    assert e in ["+","-"]

    prefix="amplitude "
    outputStrs=[]
    for c in ["Re","Im"]:
        outputStr = prefix
        outputStr += constructWaveString(l,m,e,c,"LOOPREAC")
        outputStr+=" Zlm "
        waveValues=[str(l), str(m)]
        if e=="+" and c=="Re":
            waveValues+=["+1","+1"]
        if e=="+" and c=="Im":
            waveValues+=["-1","-1"]
        if e=="-" and c=="Re":
            waveValues+=["+1","-1"]
        if e=="-" and c=="Im":
            waveValues+=["-1","+1"]
        outputStr += " ".join(waveValues)
        outputStr += " LOOPPOLANG LOOPPOLVAL"
        outputStrs.append(outputStr)
    return "\n".join(outputStrs)

def initializeWave(l,m,e,anchor):
    '''
    l = Spin {0, 1, 2 ...}
    m = Spin projection {..., -2, -1, 0, 1+, 2+, ... }
    e = reflectivity {+/-}
    anchor = boolean to set this wave as the anchor, anchor wave requires wave to be positive
    '''
    prefix="initialize "
    c="Re" # since we constrain the (Re)al and (Im)aginary parts of the waves to be the same we only need to initialize one part
    outputStr = prefix
    outputStr += constructWaveString(l,m,e,c,"LOOPREAC")
    outputStr += " cartesian "
    if anchor:
        outputStr += str(random.uniform(-100,100)) + " 0.0 real"
    else:
        outputStr += str(random.uniform(-100,100)) + " " + str(random.uniform(-100,100)); 
    return outputStr

def constrainWave(l,m,e,preamble):
    '''
    l = Spin {0, 1, 2 ...}
    m = Spin projection {..., -2, -1, 0, 1+, 2+, ... }
    e = reflectivity {+/-}
    preamble = data copied over from the reference config, will be used to the fit name
    '''
    prefix="constrain "
    outputStr = prefix
    # First we constrain the Re and Im parts of a given wave
    outputStr += constructWaveString(l,m,e,"Re","LOOPREAC") + " " + constructWaveString(l,m,e,"Im","LOOPREAC")
    outputStr += "\n"
    dataset_name = [line for line in preamble.split("\n") if line.startswith("loop LOOPREAC")]
    dataset_name = dataset_name[0].split(" ")[2]
    # Second we constrain the Re/Im parts of a given wave for a given dataset to the Re/Im parts of the same wave for a different waveset
    outputStr += "constrain " + constructWaveString(l,m,e,"Re",dataset_name) + " " + constructWaveString(l,m,e,"Re","LOOPREAC")
    outputStr += "\n"
    outputStr += "constrain " + constructWaveString(l,m,e,"Im",dataset_name) + " " + constructWaveString(l,m,e,"Im","LOOPREAC")
    return outputStr

def scaleWave(l,m,e):
    '''
    l = Spin {0, 1, 2 ...}
    m = Spin projection {..., -2, -1, 0, 1+, 2+, ... }
    e = reflectivity {+/-}
    '''
    prefix="scale "
    outputStrs=[]
    for c in ["Re","Im"]:
        outputStr = prefix
        outputStr += constructWaveString(l,m,e,c,"LOOPREAC") + " LOOPSCALE"
        outputStrs.append(outputStr)
    return "\n".join(outputStrs)
    
def writeWave(l,m,e,anchor,preamble):
    '''
    l = Spin {0, 1, 2 ...}
    m = Spin projection {..., -2, -1, 0, 1+, 2+, ... }
    e = reflectivity {+/-}
    anchor = boolean to set this wave as the anchor, anchor wave requires wave to be positive
    '''
    outputList=[
            defineWave(l,m,e),
            initializeWave(l,m,e,anchor),
            constrainWave(l,m,e,preamble),
            scaleWave(l,m,e)
            ]
    return "\n".join(outputList)

def constructOutputFileName(lmes,i=-1):
    mapLtoSpect={0:"S",1:"P",2:"D"};
    names=[mapLtoSpect[lme[0]]+str(lme[1])+lme[2] for lme in lmes]
    cfgFileName="_".join(names)
    if i==-1:
        return cfgFileName
    else:
        return cfgFileName+"("+str(i)+").cfg"

def writeCfg(lmes,reference_file,seed,i):
    '''
    lmes: List of lists. Each sublist is in the [l,m,e,anchor] format
    reference_file: we will get our preamble from here
    seed: set the random seed we will sample from to initialize our waveset
    i: iteration number, we should set this when doing multiple fits with random initializations
    '''
    with open(reference_file,"r") as ref:
        '''
        We will be very specific on what we write to the new config file. We will
        remove all commented lines and remove all lines that deal with setting up
        the partial waves. We will also remove repeated new lines
        '''
        preamble=ref.readlines()
        preamble=[line for line in preamble if not line.startswith("#")]
        preamble=[line for line in preamble if not line.startswith("amplitude")]
        preamble=[line for line in preamble if not line.startswith("initialize")]
        preamble=[line for line in preamble if not line.startswith("constrain")]
        preamble=[line for line in preamble if not line.startswith("scale")]

        preamble=[line.rstrip().lstrip()+"-"+str(i)+"\n" if line.startswith("fit") else line for line in preamble]

        pols = [line for line in preamble if line.startswith("loop LOOPREAC")]
        pols = pols[0].rstrip().lstrip().split(" ")[2:]
        pols = [pol.split("_")[1] for pol in pols]
        pols = "_".join(pols)

        preamble="".join(preamble)
        preamble=re.sub(r'\n+','\n',preamble).strip()

    
    waveStrings=[preamble]
    for lme in lmes:
        waveStrings.append(writeWave(*lme,preamble=preamble))
    
    # output config file name?
    cfgFileName=constructOutputFileName(lmes,i)
    #mapLtoSpect={0:"S",1:"P",2:"D"};
    #names=[mapLtoSpect[lme[0]]+str(lme[1])+lme[2] for lme in lmes]
    #cfgFileName="_".join(names)+"("+str(i)+").cfg"
    
    with open(cfgFileName,"w") as cfgFile:
        outputString="\n\n".join(waveStrings)
        outputString=outputString.replace("\r\n", os.linesep)
        cfgFile.writelines(outputString)
    return cfgFileName, pols
