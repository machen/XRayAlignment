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
        """
        self.data = pd.DataFrame(inputData, columns=['Y', 'X', 'Intensity'])
        self.data = self.data.sort_values(by=['Y',  'X'])
        self.mapDim = [0, 0]
        xData = inputData[0]
        xSmooth = np.round(xData, decimals=3)  # Smooth data to micron accuracy
        self.mapDim[1] = len(xSmooth.unique())
        yData = inputData[1]
        ySmooth = np.round(yData, decimals=3)  # Smooth data to micron accuracy
        intData = inputData[2]
        self.mapDim[0] = len(ySmooth.unique())
        self.intensities = pd.DataFrame(np.reshape(intData,
                                        newshape=self.mapDim, order='C'))
        self.x = pd.DataFrame(np.reshape(xSmooth, newshape=self.mapDim,
                                         order='C'))
        self.y = pd.DataFrame(np.reshape(ySmooth, newshape=self.mapDim,
                                         order='C'))
        self.element = element
        self.timePoint = timePoint

    def subSelect(self, xmin, xmax, ymin, ymax):
        """Function should sub-select the intensity, x, and y matrices"""
        xSection = self.x.loc[0, (self.x.loc[0, :] > xmin) &
                                 (self.x.loc[0, :] < xmax)]
        ySection = self.y.loc[(self.y.loc[:, 0] > ymin) &
                              (self.y.loc[:, 0] < ymin), 0]
        xRes = self.x.loc[ySection, xSection]
        yRes = self.y.loc[ySection, xSection]
        intRes = self.intensities.loc[ySection, xSection]
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


plt.ion()

# Step 1: Select the files from the region that we want to examine

dataFileLocation = """C:\\Users\\Michael\\OneDrive\\Archive\\MIT Grad School Research Overflow\\Microfluidics\\NSLS-II Data\\Kocar_NSLS-II_October15_2018_EndOfRun\\01010_Kocar\\Maps\\Exported Data\\Device 6G Normalized by I0\\"""
region = "Region2"  # CHANGE THIS
rinseAdjust = [-0.03, 0.01]  # Adjustment to align AGWRinse with AsFilled [x, y] in mm
sulfideAdjust = [-0.045, 0.01]  # Adjustment to align SulfideFlush with AsFilled
timePoints = ["AGWRinse", "AsFilled", "SFlush"]
availableFiles = os.listdir(dataFileLocation)
data = pd.DataFrame(columns=["Time Point", "Element", "X", "Y", "Intensity"])
