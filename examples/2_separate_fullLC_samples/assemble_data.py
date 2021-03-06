"""
Developed by the CRP #4 team. 
CRP #4 was held in Clermont Ferrand, France in August 2017.

This script separates the SNPCC photometric data into a query
and a validation sample.

Training data are not change, just format is corrected.
"""


import numpy as np
from actsnclass import read_snana_lc

# set random seeds
np.random.seed(137*231+23*17+2*54*11+7)
np.random.random_sample(2317)

# set proportion of data to be left out for final result
publishDataProportion=0.33

# read fluxes
dataMatrixPhoto = np.genfromtxt('../data/photo_fitparameters.dat', delimiter=' ')
dataMatrixSpec = np.genfromtxt('../data/spec_fitparameters.dat', delimiter=' ')

dataMatrix = list(dataMatrixPhoto)
for line in dataMatrixSpec:
    dataMatrix.append(line)

dataMatrix = np.array(dataMatrix)

# read ids
op1 = open('../data/photo_labels.dat', 'r')
lin1 = op1.readlines()
op1.close()

snidPhoto = [[elem.split()[0]] for elem in lin1[1:]]

op2 = open('../data/spec_labels.dat', 'r')
lin2 = op2.readlines()
op2.close()

snidSpec = [[elem.split()[0]] for elem in lin2[1:]]

snid = snidPhoto
for line in snidSpec:
    snid.append(line)


for line in snid:
    print snid.index(line)

    snlc = read_snana_lc('../../data/SIMGEN_PUBLIC_DES/' + line[0] + '.DAT')
    line.append(snlc[0]['sample'])
    line.append(snlc[0]['type'][0])
    
dataLabels = np.array(snid)

# clean data
infRows=np.any(np.isinf(dataMatrix),axis=1)

nanRows=np.any(np.isnan(dataMatrix),axis=1)

zeroRows=np.full(dataMatrix.shape[0],False,dtype=bool)

for i in range(4):
    
    idFrom=i*int(dataMatrix.shape[1]/4)
    idTo=(i+1)*int(dataMatrix.shape[1]/4)
    
    zeroRows=np.logical_or(zeroRows, np.amax(dataMatrix[:,idFrom:idTo], axis=1)==0)
    
goodRows=np.logical_not(np.logical_or(np.logical_or(infRows,zeroRows),nanRows))

dataMatrix=dataMatrix[goodRows]
dataLabels=dataLabels[goodRows]

trainIndices=dataLabels[:,1]=='train'


trainingSet=dataMatrix[trainIndices]
trainingLabels=dataLabels[trainIndices]

remainingSet=dataMatrix[np.logical_not(trainIndices)]
remainingLabels=dataLabels[np.logical_not(trainIndices)]

inds = np.arange(len(remainingSet))
np.random.shuffle(inds)

publishSet=remainingSet[inds[:int(publishDataProportion*len(remainingSet))]]
publishLabels=remainingLabels[inds[:int(publishDataProportion*len(remainingSet))]]

crossValidationSet=remainingSet[inds[int(publishDataProportion*len(remainingSet)):]]
crossValidationLabels=remainingLabels[inds[int(publishDataProportion*len(remainingSet)):]]

                              
np.savetxt('../data/train_fitparameters.dat', trainingSet, fmt="%.8f", header='33 fluxes for g,r,i,z')
np.savetxt('../data/train_labels.dat', trainingLabels, fmt="%s", header='ID train/target Class')                                     
                                    
np.savetxt('../data/query_fitparameters.dat', crossValidationSet, fmt="%.8f", header='33 fluxes for g,r,i,z')
np.savetxt('../data/query_labels.dat', crossValidationLabels, fmt="%s", header='ID train/target Class')
                                      
np.savetxt('../data/target_fitparameters.dat', publishSet, fmt="%.8f", header='33 fluxes for g,r,i,z')
np.savetxt('../data/target_labels.dat', publishLabels, fmt="%s", header='ID train/target Class')

