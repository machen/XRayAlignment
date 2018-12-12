import numpy as np
import pandas as pd
import os
import re

# Step 1: Select the files from the region that we want to examine

dataFileLocation = """C:\\Users\\Michael\\OneDrive\\Archive\\MIT Grad School Research Overflow\\Microfluidics\\NSLS-II Data\\Kocar_NSLS-II_October15_2018_EndOfRun\\01010_Kocar\\Maps\\Exported Data\\Device 6G Normalized by I0\\"""
region = "Region1"  # CHANGE THIS
timePoints = ["AGWRinse", "AsFilled", "SFlush"]
availableFiles = os.listdir(dataFileLocation)
data = pd.DataFrame(columns=["Time Point", "Element", "X", "Y", "Intensity"])

for timePoint in timePoints:
    # Selects for files that match the region and timepoint of interest
    filePat = re.compile(".*_("+timePoint+")_("+region+")_.*_(\D{2})_Ka.dat")
    for name in availableFiles:
        match = re.match(filePat, name)
        if match:
            newData = pd.read_table(dataFileLocation+name, skiprows=[0,1,2],
                                    header=None, names=['Y', 'X', 'Intensity'],
                                    sep="\s+")
            newData.loc[:, "Time Point"] = timePoint
            newData.loc[:, "Element"] = match.group(3)
            data = data.append(newData, ignore_index=True)

# Apply calculated displacements to data
fillingData = data.loc[:, data.loc[:, "Time Point"=="AsFilled"]]
# fillingData = fillingData.loc[:, ["X", "Y", "Intensity"]].values
rinseData = data.loc[:, data.loc[:, "Time Point"=="AGWRinse"]]
rinseData.loc[:, "X"] = rinseData.loc[:, "X"]+0.025
rinseData.loc[:, "Y"] = rinseData.loc[:, "Y"]-0.005
# rinseData = rinseData.loc[:, ["X", "Y", "Intensity"]].values
sulfideData = data.loc[:, data.loc[:, "Time Point"=="SFlush"]]
sulfideData.loc[:, "X"] = sulfideData.loc[:, "X"]+0.040
sulfideData.loc[:, "Y"] = sulfideData.loc[:, "Y"]-0.01
# sulfideData = sulfideData.loc[:, ["X", "Y", "Intensity"]].values


#Calculate differences
difference = pd.DataFrame(columns=["X","Y","FillingRinse","RinseSulfide"])
for row in fillingData.iterrows():
    X = row["X"]
    Y = row["Y"]
    element = row["Element"]
    fillIntensity = row["Intensity"]
    # Calculate Filling Minus Rinse
    subData = rinseData.loc[:, rinseData.loc[:,"Element"==element]]
    subData = subData.loc[abs(subData.loc[:,'X']-X)<0.004,:]
    subData = subData.loc[abs(subData.loc[:,'Y']-Y)<0.004,:]
    res = len(subData)
    if res == 1:
        rinseIntensity = subData.loc[:, "Intensity"]
    elif res == 0:
        continue
