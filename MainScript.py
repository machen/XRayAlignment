import numpy as np
import pandas as pd
import os
import re

# Step 1: Select the files from the region that we want to examine

dataFileLocation = """C:\\Users\\Michael\\OneDrive\\Archive
                      \\MIT Grad School Research Overflow\\Microfluidics
                      \\NSLS-II Data\\Kocar_NSLS-II_October15_2018_EndOfRun
                      \\01010_Kocar\\Maps\\Exported Data
                      \\Device 6G Normalized by I0"""
region = "Region1"  # CHANGE THIS
timePoints = ["AGWRinse", "AsFilled", "SFlush"]
availableFiles = os.listdir(dataFileLocation)
for timePoint in timePoints:
    # Selects for files that match the region and timepoint of interest
    filePat = re.compile(".*_("+timePoint+")_("+region+")_.*_(\D{2})_Ka.dat")
    for name in availableFiles:
