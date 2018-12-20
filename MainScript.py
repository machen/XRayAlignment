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
        self.data = pd.DataFrame(inputData, columns=['Y','X','Intensity'])
        self.mapDim = [0, 0]
        xData = inputData[0]
        xSmooth = np.round(xData, decimals=3)  # Smooth data to micron accuracy
        self.mapDim[1] = len(xSmooth.unique())
        yData = inputData[1]
        ySmooth = np.round(yData, decimals=3)  # Smooth data to micron accuracy
        intData = inputData[2]
        self.mapDim[0] = len(ySmooth.unique())
        self.intensities = np.reshape(intData, newshape=self.mapDim, order='C')
        self.x = np.reshape(xSmooth, newshape=self.mapDim, order='C')
        self.y = np.reshape(ySmooth, newshape=self.mapDim, order='C')
        self.element = element
        self.timePoint = timePoint

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
