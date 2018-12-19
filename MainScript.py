import numpy as np
import pandas as pd
import os
import re
import matplotlib.pyplot as plt


class dataMap():
    def __init__(self, inputData, element, timePoint):
        """Input data format:
        Example for a 3,2 map
        Y X Intensity
        yVal1 xVal1 intVal1
        yVal1 xVal2 intVal2
        yVal2 xVal1 intVal3
        yVal2 xVal2 intVal4
        yVal3 xVal2 intVal5
        yVal3 xVal2 intVal6

        Might be worthwhile to set it up so that the matrix comes pre sorted
        """
        self.mapDim = [0, 0]
        xData = inputData[0]
        xSmooth = np.round(xData, decimals=3)  # Smooth data to micron accuracy
        self.mapDim[1] = len(xSmooth.unique())
        yData = inputData[1]
        ySmooth = np.round(yData, decimals=3)  # Smooth data to micron accuracy
        intData = inputData[2]
        self.mapDim[0] = len(ySmooth.unique())
        self.intensities = np.reshape(intData, newshape=self.mapDim)
        self.x = np.reshape(xSmooth, newshape=self.mapDim, order='C')
        self.y = np.reshape(ySmooth, newshape=self.mapDim, order='C')
        self.element = element
        self.timePoint = timePoint



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
region = "Region2"  # CHANGE THIS
rinseAdjust = [-0.03, 0.01]  # Adjustment to align AGWRinse with AsFilled [x, y] in mm
sulfideAdjust = [-0.045, 0.01]  # Adjustment to align SulfideFlush with AsFilled
timePoints = ["AGWRinse", "AsFilled", "SFlush"]
availableFiles = os.listdir(dataFileLocation)
data = pd.DataFrame(columns=["Time Point", "Element", "X", "Y", "Intensity"])

# Better option would be to have data pre set up in matrices, or write a method that auto converts a list to a matrix and vice versa

#Also how do multi-indexes work? That seems like something that might work...

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
    plt.imshow(asMap, cmap='RdBu', vmin=-0.003, vmax=0.003)
    plt.title("Difference between AGW Rinse and As Filling: {}".format(ele))
    plt.colorbar()

    asMap = subData.loc[:, 'RinseSulfide'].values.reshape(mapSize)
    f2 = plt.figure(2*i+2)
    plt.imshow(asMap, cmap='RdBu', vmin=-0.003, vmax=0.003)
    plt.title("Difference between Sulfide Rinse and AGW Rinse: {}".format(ele))
    plt.colorbar()

