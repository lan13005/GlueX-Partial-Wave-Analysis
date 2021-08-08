#!/usr/bin/env python
# coding: utf-8

# In[26]:


import uproot3 as uproot
import pandas
import numpy as np
import matplotlib.pyplot as plt


# In[33]:


degToRad=3.14159/180
polMagMap={
    "000":0.3519,
    "045":0.3374,
    "090":0.3303,
    "135":0.3375,
    "AMO":0.00001
}
polMagMap2={
    0:0.3519,
    45:0.3374,
    90:0.3303,
    135:0.3375,
    -1:0.00001
}
polAngMap={
    "000":0.0*degToRad,
    "045":45.0*degToRad,
    "090":90.0*degToRad,
    "135":135*degToRad,
    "AMO":0.0*degToRad
}
polMap={
    0:"000",
    45:"045",
    90:"090",
    135:"135",
    -1:"AMO"
}

variables=["event","cosTheta_eta_hel","phi_eta_hel","mandelstam_t","Mpi0eta","weightASBS","Phi","BeamAngle"]
mapNames={"event"}


# In[54]:


#############################
# Load all the data
#############################

dataTags=["2018_8"] #["2017","2018_1","2018_8"]
mapDataset={}

for dataFormat in [""]:#["data","flat"]:
    print("NEXT FORMAT: "+dataFormat+"-----------------\n\n")
    datas=[]
    trees=[]
    dfs=[]

    totalEvents=0
    for i,dataTag in enumerate(dataTags):
#        fileloc="/d/grid17/ln16/myDSelector/degALL_malte_kmatrix_2018_8_mEllipse_8288_tLT1_chi13_omegacut_treeFlat_DSelector.root"
#        treename="degALL_malte_kmatrix_2018_8_mEllipse_8288_tLT1_chi13_omegacut_tree_flat"
        fileloc="/d/grid17/ln16/myDSelector/degALL_flat_2018_8_mEllipse_8288_chi13_tLT1_omegacut_treeFlat_DSelector.root"
        treename="tree_4g_flat"
        datas.append(uproot.open(fileloc))
        trees.append(datas[i][treename])
        dfs.append(trees[i].arrays(variables,outputtype=pandas.DataFrame))

        dfs[i].rename(
            columns={
            "event":"EventN",
            "cosTheta_eta_hel":"theta",
            "phi_eta_hel":"phi",
            "mandelstam_t":"tM",
            "Mpi0eta":"mass",
            "Phi":"alpha",
            "BeamAngle":"beamAngle"
            },
            inplace=True)

        # When looking at simulation, it is possible to fix the beam angle. the beamAngle from the trees would look
        #   at ccdb for the run information. This would not be what was simulated
#        dfs[i].beamAngle=0

        # Adding some branches to the dataset
        dfs[i]["pol"]=dfs[0].beamAngle.map(polMagMap2)

        print("{0} has {1} events".format(dataTag,len(dfs[i])))
        totalEvents+=len(dfs[i])


    #############################
    # Split weights and data
    #############################
    # Fix some columns
    phase1_data=pandas.concat(dfs)
    print("total events {0}".format(totalEvents))
    phase1_data.theta=np.arccos(phase1_data.theta)
    phase1_data.phi=np.radians(phase1_data.phi)
    phase1_data.alpha=np.radians(phase1_data.alpha)
    phase1_data.tM = -1*phase1_data.tM
    
    # apply any cuts
    phase1_data=phase1_data[phase1_data.weightASBS!=0]
    cut_tLT01GT03=(abs(phase1_data.tM)>0.1)&(abs(phase1_data.tM)<0.3)
    phase1_data=phase1_data[cut_tLT01GT03]
    print("total events after some more selections {0}".format(len(phase1_data)))

    
    for ipol,pol in enumerate([0,45,90,135,-1]):
    #for ipol,pol in enumerate([0]):
        # apply any final cuts
        phase1_data_subset = phase1_data[phase1_data.beamAngle==pol]
        phase1_data_subset.beamAngle = np.radians(phase1_data_subset.beamAngle)
        print("After cuts (pol=={}): {}".format(pol,phase1_data_subset.shape))
        
        phase1_data_subset.reset_index(drop="true")

        # Split weight and data columns
        phase1_weight_subset=phase1_data_subset[["weightASBS","mass"]]
        phase1_data_subset=phase1_data_subset.drop("weightASBS",axis=1)
    
        #############################
        # Write to csvs
        #############################
#        phase1_weight_subset.to_csv("malte_kmatrix_weights.csv",index=False)
#        phase1_data_subset.to_csv("malte_kmatrix_data.csv",index=False)
        phase1_data_subset.to_csv("flat_2018_8_data_"+polMap[pol]+".csv",index=False)
        phase1_weight_subset.to_csv("flat_2018_8_weights_"+polMap[pol]+".csv",index=False)


# In[ ]:




