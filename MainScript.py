import numpy as np
import pandas as pd
import os
import re

# Step 1: Select the files from the region that we want to examine

dataFileLocation = """C:\\Users\\Michael\\OneDrive\\Archive\\MIT Grad School Research Overflow\\Microfluidics\\NSLS-II Data\\Kocar_NSLS-II_October15_2018_EndOfRun\\01010_Kocar\\Maps\\Exported Data\\Device 6G Normalized by I0\\"""
region = "Region1"  # CHANGE THIS
rinseAdjust = [0.025, -0.005]  # Adjustment to align AGWRinse with AsFilled [x, y] in mm
sulfideAdjust = [0.040, -0.01]  # Adjustment to align SulfideFlush with AsFilled
timePoints = ["AGWRinse", "AsFilled", "SFlush"]
availableFiles = os.listdir(dataFileLocation)
data = pd.DataFrame(columns=["Time Point", "Element", "X", "Y", "Intensity"])

for timePoint in timePoints:
    # Selects for files that match the region and timepoint of interest
    filePat = re.compile(".*_("+timePoint+")_("+region+")_.*_(\D{2})_Ka.dat")
    for name in availableFiles:
        match = re.match(filePat, name)
        if match:
            newData = pd.read_table(dataFileLocation+name, skiprows=[0, 1, 2],
                                    header=None, names=['Y', 'X', 'Intensity'],
                                    sep="\s+")
            newData.loc[:, "Time Point"] = timePoint
            newData.loc[:, "Element"] = match.group(3)
            data = data.append(newData, ignore_index=True)
data = data.round({'X': 3, 'Y': 3})
# Apply calculated displacements to data
fillingData = data.loc[data.loc[:, "Time Point"] == "AsFilled", :]
# fillingData = fillingData.loc[:, ["X", "Y", "Intensity"]].values
rinseData = data.loc[data.loc[:, "Time Point"] == "AGWRinse", :]
rinseData.loc[:, "X"] = rinseData.loc[:, "X"]+rinseAdjust[0]
rinseData.loc[:, "Y"] = rinseData.loc[:, "Y"]+rinseAdjust[1]
# rinseData = rinseData.loc[:, ["X", "Y", "Intensity"]].values
sulfideData = data.loc[data.loc[:, "Time Point"] == "SFlush", :]
sulfideData.loc[:, "X"] = sulfideData.loc[:, "X"]+sulfideAdjust[0]
sulfideData.loc[:, "Y"] = sulfideData.loc[:, "Y"]+sulfideAdjust[1]
# sulfideData = sulfideData.loc[:, ["X", "Y", "Intensity"]].values


# Calculate differences

differenceMat = []
for i in fillingData.index:
    X = fillingData.loc[i, "X"]
    Y = fillingData.loc[i, "Y"]
    element = fillingData.loc[i, "Element"]
    fillIntensity = fillingData.loc[i, "Intensity"]
    # Calculate Filling Minus Rinse, first select for the coordinate
    subData = rinseData.loc[rinseData.loc[:, "Element"] == element, :]
    subData = subData.loc[(abs(subData.loc[:,
                          'X']-X) < 0.0001) & (abs(subData.loc[:,
                          'Y']-Y) < 0.0001), :]
    point = subData.index
    res = len(subData)
    # Test to make sure we have the correct amount
    if res == 1:
        rinseIntensity = float(subData.loc[point, "Intensity"])
    elif res == 0:
        continue
    else:
        raise ValueError('Non-unique results during coordinate search')

    subData = sulfideData.loc[sulfideData.loc[:, "Element"] == element, :]
    subData = subData.loc[(abs(subData.loc[:,
                               'X']-X) < 0.0001) & (abs(subData.loc[:,
                               'Y']-Y) < 0.0001), :]
    point = subData.index
    res = len(subData)
    if res == 1:
        sulfideIntensity = float(subData.loc[point, "Intensity"])
    elif res == 0:
        continue
    else:
        raise ValueError('Non-unique results during coordinate search')
    differenceMat.append([X, Y, rinseIntensity - fillIntensity,
                          sulfideIntensity - rinseIntensity, element])
    print(i)
difference = pd.DataFrame(differenceMat, columns=["X", "Y", "FillingRinse",
                          "RinseSulfide", "element"])
