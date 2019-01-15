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

        It must be presorted by Y then X, and should be inputted as a dataframe
        """
        self.mapDim = [0, 0]
        xData = inputData.loc[:, 'X']
        xSmooth = np.round(xData, decimals=3)  # Smooth data to micron accuracy
        self.mapDim[1] = len(xSmooth.unique())
        yData = inputData.loc[:, 'Y']
        ySmooth = np.round(yData, decimals=3)  # Smooth data to micron accuracy
        intData = inputData.loc[:, "Intensity"]
        self.mapDim[0] = len(ySmooth.unique())
        self.intensities = pd.DataFrame(np.reshape(intData.values,
                                        newshape=self.mapDim, order='C'))
        self.x = pd.DataFrame(np.reshape(xSmooth.values, newshape=self.mapDim,
                                         order='C'))
        self.y = pd.DataFrame(np.reshape(ySmooth.values, newshape=self.mapDim,
                                         order='C'))
        self.element = element
        self.timePoint = timePoint
        self.xshift = 0.0
        self.yshift = 0.0
        self.xRng = [min(self.x), max(self.x)]
        self.yRng = [min(self.y), max(self.y)]

    def __repr__(self):
        return "Timepoint: {}, Element: {}, Map Dimensions: {}".format(self.timePoint, self.element, self.mapDim)

    def mapShift(self, shiftParams):
        self.x += shiftParams[0]
        self.y += shiftParams[1]
        self.xshift += shiftParams[0]
        self.yshift += shiftParams[1]
        return

    def subSelect(self, xmin, xmax, ymin, ymax):
        """Function should sub-select the intensity, x, and y matrices"""
        xSection = self.x.loc[:, (self.x.loc[0, :] >= xmin) &
                                 (self.x.loc[0, :] <= xmax)]
        ySection = self.y.loc[(self.y.loc[:, 0] >= ymin) &
                              (self.y.loc[:, 0] <= ymax), :]

        if xSection.empty or ySection.empty:
            return [], [], []
        xRes = self.x.loc[ySection.index, xSection.columns]
        yRes = self.y.loc[ySection.index, xSection.columns]
        intRes = self.intensities.loc[ySection.index, xSection.columns]
        return xRes, yRes, intRes

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def getInt(self):
        return self.intensities

    def getTime(self):
        return self.timePoint

    def getElement(self):
        return self.element

    def getMapDim(self):
        return self.mapDim


def mapSubtract(dataMap1, dataMap2):
    x1 = dataMap1.getX().values
    x2 = dataMap2.getX().values
    y1 = dataMap1.getY().values
    y2 = dataMap2.getY().values
    # Something wrong with how max/min is working. Check into it.
    xmin = np.max([np.min(x1, axis=(0, 1)), np.min(x2, axis=(0, 1))])
    ymin = np.max([np.min(y1, axis=(0, 1)), np.min(y2, axis=(0, 1))])
    xmax = np.min([np.max(x1, axis=(0, 1)), np.max(x2, axis=(0, 1))])
    ymax = np.min([np.max(y1, axis=(0, 1)), np.max(y2, axis=(0, 1))])
    xMatch1, yMatch1, intMatch1 = dataMap1.subSelect(xmin, xmax, ymin, ymax)
    xMatch2, yMatch2, intMatch2 = dataMap2.subSelect(xmin, xmax, ymin, ymax)
    import pdb; pdb.set_trace()  # breakpoint 1e985020 //

    if xMatch1.shape != xMatch2.shape:
        # Need to decide how to handle if subSelect isn't working correctly, or if data has incompatible resolutions
        print([xMatch1.shape, xMatch2.shape])
        raise ValueError("The arrays are not the same shape")
    xDiff = xMatch2.values-xMatch1.values
    yDiff = yMatch2.values-yMatch1.values
    intDiff = intMatch2.values-intMatch1.values

    return xDiff, yDiff, intDiff


plt.ion()

# Step 1: Select the files from the region that we want to examine

dataFileLocation = """C:\\Users\\Michael\\OneDrive\\Archive\\MIT Grad School Research Overflow\\Microfluidics\\NSLS-II Data\\Kocar_NSLS-II_October15_2018_EndOfRun\\01010_Kocar\\Maps\\Exported Data\\Device 6G Normalized by I0\\"""
region = "Region3"  # CHANGE THIS
rinseAdjust = [-0.03, 0.005]  # Adjustment to align AGWRinse with AsFilled [x, y] in mm
sulfideAdjust = [-0.045, 0.01]  # Adjustment to align SulfideFlush with AsFilled
timePoints = ["AGWRinse", "AsFilled", "SFlush"]
availableFiles = os.listdir(dataFileLocation)

data = {}

# Load in data to main dictionary
"""data is a dictionary of the collected timepoint maps,
   with keys as the time point labels
   Each entry then is a dictionary of the dataMap objects,
   with the relevant element as keys"""

for timePoint in timePoints:
    # Selects for files that match the region and timepoint of interest
    filePat = re.compile(".*_("+timePoint+")_("+region+")_.*_(\D{2})_Ka.dat")
    maps = {}
    for name in availableFiles:
        match = re.match(filePat, name)
        if match:
            newData = pd.read_table(dataFileLocation+name, skiprows=[0, 1, 2],
                                    header=None, names=['Y', 'X', 'Intensity'],
                                    sep="\s+")
            newData.sort_values(by=['Y',  'X'])
            maps[match.group(3)] = dataMap(newData, match.group(3), timePoint)
    data[timePoint] = maps

# Apply shifts to relevant data
for element in data['AGWRinse']:
    data['AGWRinse'][element].mapShift(rinseAdjust)


for element in data['SFlush']:
    data['SFlush'][element].mapShift(sulfideAdjust)

# Generate the relevant difference maps
i = 0

for element in data['AsFilled']:
    fillData = data['AsFilled'][element]
    rinseData = data['AGWRinse'][element]
    rinseDiffX, rinseDiffY, rinseDiffInt = mapSubtract(fillData, rinseData)
    f1 = plt.figure(2*i+1)
    ax1 = f1.add_subplot(1, 2, 1)
    ax2 = f1.add_subplot(2, 2, 2)
    ax3 = f1.add_subplot(2, 2, 4)
    ax1.imshow(rinseDiffInt, cmap='RdBu', vmin=-0.001, vmax=0.001)
    ax1.set_title('{} Change after rinsing with AGW'.format(element))
    ax2.imshow(rinseDiffX, cmap='RdBu', vmin=-0.001, vmax=0.001)
    ax3.imshow(rinseDiffY, cmap='RdBu', vmin=-0.001, vmax=0.001)
    # PLOT THE DIFFERNCES LABEL THE FIGURE
    # MAYBE STATS ON THE FIGURES AS WELL
    sulfideData = data['SFlush'][element]
    sulfideDiffX, sulfideDiffY, sulfideDiffInt = mapSubtract(rinseData,
                                                             sulfideData)
    f2 = plt.figure(2*i+2)
    ax1 = f2.add_subplot(1, 2, 1)
    ax2 = f2.add_subplot(222)
    ax3 = f2.add_subplot(224)
    ax1.imshow(sulfideDiffInt, cmap='RdBu', vmin=-0.001, vmax=0.001)
    ax1.set_title('{} Change after Addition of Sulfide'.format(element))
    ax2.imshow(sulfideDiffX, cmap='RdBu', vmin=-0.001, vmax=0.001)
    ax3.imshow(sulfideDiffY, cmap='RdBu', vmin=-0.001, vmax=0.001)
    # PLOT THE DIFFERENCES LABEL THE FIGURE
    # MAYBE STATS ON THE FIGURES AS WELL
    i+=1
