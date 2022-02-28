#####
# fitAndDraw should do both fitting and drawing. Good for running over night but Draw.py will use multiprocessing to try and just Draw faster
####


import os
import multiprocessing

#ts=["010016", "016021", "021027", "027034", "034042", "042051", "051061", "061072", "072085", "085100"]
ts=["010020", "0200325", "0325050", "050075", "075100"]

def draw(t):
    os.chdir(t)

    waves=[
        "S0+-_S0++_D1--_D0+-_D1+-_D0++_D1++_D2++_pD1--_pD0+-_pD1+-_pD0++_pD1++_pD2++",
        "S0+-;S0++", # S waves
        "D1--;D0+-;D1+-;D0++;D1++;D2++", # D waves  
        "pD1--;pD0+-;pD1+-;pD0++;pD1++;pD2++", # D prime
        "S0+-_S0++", #sum S waves
        "D1--_D0+-_D1+-_D0++_D1++_D2++", #sum D waves
        "pD1--_pD0+-_pD1+-_pD0++_pD1++_pD2++", #sum D prime waves
    ]
    waves=";".join(waves)

    cmd="python3 ../overlayBins.py 2 '"+wave+"' 'etapi0_SD_TMD_piecewise_update.fit' '..'"
    os.system(cmd)
    os.chdir("..")

with multiprocessing.Pool(5) as p:
    p.map(draw,ts)
