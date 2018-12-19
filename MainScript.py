import numpy as np
import pandas as pd
import os
import re
import matplotlib.pyplot as plt


def subSelect(data, xmin, xmax, ymin, ymax):
    """Takes dataFrame with X and Y columns, and sub-selects so that it only
     contains coordinates in the specified x/y ranges"""
    res = data.loc[(data.loc[:, 'X'] > xmin) & (data.loc[:, 'X'] < xmax), :]
    res = res.loc[(data.loc[:, 'Y'] > ymin) & (data.loc[:, 'Y'] < ymax), :]
    res = res.sort_values(by=['Element', 'X', 'Y'])
    # Think there should be a line to force sorting of the matrix (ie x then y)
    return res


plt.ion()

# Step 1: Select the files from the region that we want to examine

dataFileLocation = """C:\\Users\\Michael\\OneDrive\\Archive\\MIT Grad School Research Overflow\\Microfluidics\\NSLS-II Data\\Kocar_NSLS-II_October15_2018_EndOfRun\\01010_Kocar\\Maps\\Exported Data\\Device 6G Normalized by I0\\"""
region = "Region4"  # CHANGE THIS
rinseAdjust = [0.03, -0.005]  # Adjustment to align AGWRinse with AsFilled [x, y] in mm
sulfideAdjust = [0.04, -0.01]  # Adjustment to align SulfideFlush with AsFilled
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
rinseData.loc[:, "X"] = rinseData.loc[:, "X"]-rinseAdjust[0]
rinseData.loc[:, "Y"] = rinseData.loc[:, "Y"]-rinseAdjust[1]
# rinseData = rinseData.loc[:, ["X", "Y", "Intensity"]].values
sulfideData = data.loc[data.loc[:, "Time Point"] == "SFlush", :]
sulfideData.loc[:, "X"] = sulfideData.loc[:, "X"]-sulfideAdjust[0]
sulfideData.loc[:, "Y"] = sulfideData.loc[:, "Y"]-sulfideAdjust[1]
# sulfideData = sulfideData.loc[:, ["X", "Y", "Intensity"]].values


# Calculate differences: current method iterates over all of the available points

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
                          sulfideIntensity - rinseIntensity, element,
                          fillIntensity, rinseIntensity, sulfideIntensity])
    print([X, Y, element])

# An alternate method would be to select out the ranges that have the same values, and align them.

# Data does not appear to be well behaved enough to work

# Pick map region that aligns everything

# xmin = max([min(fillingData.loc[:, 'X']), min(rinseData.loc[:, 'X']),
#             min(sulfideData.loc[:, 'X'])])
# xmax = min([max(fillingData.loc[:, 'X']), max(rinseData.loc[:, 'X']),
#             max(sulfideData.loc[:, 'X'])])

# ymin = max([min(fillingData.loc[:, 'Y']), min(rinseData.loc[:, 'Y']),
#             min(sulfideData.loc[:, 'Y'])])
# ymax = min([max(fillingData.loc[:, 'Y']), max(rinseData.loc[:, 'Y']),
#             max(sulfideData.loc[:, 'Y'])])

# # # Filter filling data to obtain X, Y, fillingInt coordinates

# subData = subSelect(fillingData, xmin, xmax, ymin, ymax)
# xVals = subData.loc[:, 'X'].values
# yVals = subData.loc[:, 'Y'].values
# elements = subData.loc[:, 'Element'].values
# fillingInt = subData.loc[:, 'Intensity'].values

# subData = subSelect(rinseData, xmin, xmax, ymin, ymax)
# rinseInt = subData.loc[:, 'Intensity'].values

# subData = subSelect(sulfideData, xmin, xmax, ymin, ymax)
# sulfideInt = subData.loc[:, 'Intensity'].values

# differenceMat = [xVals, yVals, rinseInt-fillingInt, sulfideInt-rinseInt,
#                  elements, fillingInt, rinseInt, sulfideInt]

# Difference is a list of X, Y coordinates (rounded to the nearest micron), and the corresponding difference values

difference = pd.DataFrame(differenceMat, columns=["X", "Y", "FillingRinse",
                          "RinseSulfide", "Element", "FillInt", "RinseInt",
                          "SulfideInt"])

# Plot the differences by element/time points

mapSize = [len(difference.loc[:, "Y"].unique()),
           len(difference.loc[:, "X"].unique())]

availableElements = difference.loc[:, "Element"].unique()

for i in range(0, len(availableElements)):
    ele = availableElements[i]
    # Arsenic plots
    subData = difference.loc[difference.loc[:, "Element"] == ele, :]
    asMap = subData.loc[:, 'FillingRinse'].values.reshape(mapSize)
    f1 = plt.figure(2*i+1)
    plt.imshow(asMap, cmap='RdBu', vmin=-0.001, vmax=0.001)
    plt.title("Difference between AGW Rinse and As Filling: {}".format(ele))
    plt.colorbar()

    asMap = subData.loc[:, 'RinseSulfide'].values.reshape(mapSize)
    f2 = plt.figure(2*i+2)
    plt.imshow(asMap, cmap='RdBu', vmin=-0.001, vmax=0.001)
    plt.title("Difference between Sulfide Rinse and AGW Rinse: {}".format(ele))
    plt.colorbar()

