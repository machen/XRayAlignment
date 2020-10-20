import pandas as pd
import matplotlib.pyplot as plt

workingDir = "F:\\OneDrive\\Documents\\MIT Graduate Work\\Research\\Microfluidics\\Results\\NSLS-II Data\\Kocar_NSLS-II_October15_2018_EndOfRun\\01010_Kocar\\Maps\\Exported Data\\Device 6G Normalized by I0\\"
regionNum = 4
dataFile = "DifferenceMatrix_Region{}.csv".format(regionNum)
data = pd.read_csv(workingDir+dataFile, index_col=0)
data['fillingRinsePercent'] = data['FillingRinse'].values/data['FillInt'].values*100
data['rinseSulfidePercent'] = data['RinseSulfide'].values/data['RinseInt'].values*100

mapSize = [len(data.loc[:, "Y"].unique()),
           len(data.loc[:, "X"].unique())]

availableElements = data.loc[:, "Element"].unique()

for i in range(0, len(availableElements)):
    ele = availableElements[i]
    # Arsenic plots
    subData = data.loc[data.loc[:, "Element"] == ele, :]
    asMap = subData.loc[:, 'fillingRinsePercent'].values.reshape(mapSize)
    f1 = plt.figure(2*i+1)
    plt.imshow(asMap, cmap='RdBu', vmin=-100, vmax=100)
    plt.title("Difference between AGW Rinse and As Filling: {}".format(ele))
    plt.colorbar()

    asMap = subData.loc[:, 'rinseSulfidePercent'].values.reshape(mapSize)
    f2 = plt.figure(2*i+2)
    plt.imshow(asMap, cmap='RdBu', vmin=-100, vmax=100)
    plt.title("Difference between Sulfide Rinse and AGW Rinse: {}".format(ele))
    plt.colorbar()
plt.ion()
plt.show()