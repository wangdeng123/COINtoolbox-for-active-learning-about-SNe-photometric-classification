"""Created by CRP #4 team between 20-27 Aug 2017.

Functions to setup configuration on active learning routines.

- initialDataSetup
    Load supernova data from concatenated matrix.
"""

import copy
import numpy as np

from libact.labelers import IdealLabeler
from libact.query_strategies import RandomSampling,QueryByCommittee
from libact.query_strategies import UncertaintySampling
from libact.base.dataset import Dataset
from libact.models import SklearnAdapter, SklearnProbaAdapter

from libact.models import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier

from batchQuery import RandomBatchQuery,LeastCertainBatchQuery
from batchQuery import SemiSupervisedBatchQuery

def initialDataSetup(trainFeatures, trainClasses, testFeatures,
                     testClasses, SNLabel='0'):
    """
    Set up ideal labeler.

    input: trainFeatures, array - train matrix
           trainClasses, list - train labels
           testFeatures, array - test (photometric) matrix
           testClasses, list - test (photometric) labels
           SNLabel, str - SN Ia flag

    output: tuple, (train_dataset, fullLabels, labeler)
    """

    # Concatenate features
    fullFeatures = np.vstack([trainFeatures, testFeatures])

    # Include None in place of labels from target sample
    partialClasses = np.concatenate([(trainClasses[:,2]==SNLabel).astype(int),
                                      np.array([None] * testFeatures.shape[0])])

    # Complete concatenated labels for train and target samples
    fullClasses = np.concatenate([(trainClasses[:,2] == SNLabel).astype(int),
                                  (testClasses[:,2] == SNLabel).astype(int)])

    # Concatenate labels
    fullLabels = np.concatenate([trainClasses, testClasses])

    # Concatenated features and class labels with None on target data
    train_dataset = Dataset(fullFeatures, partialClasses)
    
    # Define ideal labeler
    labeler = IdealLabeler(Dataset(fullFeatures, fullClasses))

    return (train_dataset, fullLabels, labeler)

    
def initialModelSetup(modelID, modelParams=None, fixRandomState=False):
    
    if modelID==0:
        # Single random forest
        if modelParams is None:
            modelParams=(1000,)
        model=[SklearnProbaAdapter(RandomForestClassifier(random_state=42 \
                   if fixRandomState else None, n_estimators=modelParams[0]))]

    elif modelID==1:
        # List of random forests
        if modelParams is None:
            modelParams=(100,15)
        
        model=[SklearnProbaAdapter(RandomForestClassifier(random_state=i \
                   if fixRandomState else None, n_estimators=modelParams[0]))
                                              for i in range(modelParams[1])]

    elif modelID==2:
        # Small varied committee
        
        # SVC can be made a probabilistic model with probability=true,
        # but that slows down the fit
        
        model=[LogisticRegression(C=1.0, random_state=0 \
                                  if fixRandomState else None),
               SklearnProbaAdapter(RandomForestClassifier(n_estimators=100,
                                random_state=1 if fixRandomState else None)),
               SklearnAdapter(SVC(random_state=2 \
                                  if fixRandomState else None)),
               SklearnProbaAdapter(DecisionTreeClassifier(random_state=3 \
                                               if fixRandomState else None)),
               SklearnProbaAdapter(KNeighborsClassifier(n_neighbors=19))]
                     
    elif modelID==3:
        # Large varied committee
        
        # SVC can be made a probabilistic model with probability=true,
        # but that slows down the fit

        model=[LogisticRegression(C=1.0, 
                                  random_state=0 if fixRandomState else None),
               LogisticRegression(C=0.1, random_state=1 \
                                                 if fixRandomState else None),
               SklearnProbaAdapter(RandomForestClassifier(n_estimators=100,
                                 random_state=2 if fixRandomState else None)),
               SklearnProbaAdapter(RandomForestClassifier(n_estimators=200,
                                 random_state=3 if fixRandomState else None)),
               SklearnProbaAdapter(RandomForestClassifier(n_estimators=300,
                                 random_state=4 if fixRandomState else None)),
               SklearnProbaAdapter(RandomForestClassifier(n_estimators=400,
                                 random_state=5 if fixRandomState else None)),
               SklearnProbaAdapter(RandomForestClassifier(n_estimators=500,
                                 random_state=6 if fixRandomState else None)),
               SklearnAdapter(SVC(C=1.0,#kernel='rbf',
                                 random_state=7 if fixRandomState else None)),
               SklearnAdapter(SVC(C=0.1,kernel='rbf',
                                 random_state=8 if fixRandomState else None)),
               SklearnAdapter(SVC(C=1.0,kernel='poly', degree=3,
                                random_state=9 if fixRandomState else None)),
               SklearnAdapter(SVC(C=0.1,kernel='poly', degree=3,
                               random_state=10 if fixRandomState else None)),
               SklearnProbaAdapter(DecisionTreeClassifier(random_state=11 
                                               if fixRandomState else None)),
               SklearnProbaAdapter(KNeighborsClassifier(n_neighbors=19, 
                                                        weights='distance')),
               SklearnProbaAdapter(KNeighborsClassifier(n_neighbors=19)),
               SklearnProbaAdapter(KNeighborsClassifier(n_neighbors=9))
               ]

    return model
    
def initialQuerySetup(train_dataset, queryStrategyID,
                      queryParams=None, fixRandomState=False):

    if queryStrategyID==0:
        queryStrategy = RandomSampling(train_dataset,random_state=137 \
                                       if fixRandomState else None)

    elif queryStrategyID==1:
        queryStrategy = UncertaintySampling(train_dataset,
                                 method='sm', model=queryParams[0])

    elif queryStrategyID==2:    
        queryStrategy = QueryByCommittee(train_dataset,
                                         models=queryParams[0],
                                         disagreement='vote',
                                         random_state=23 \
                                         if fixRandomState else None)              
    elif queryStrategyID==3:
        queryStrategy = RandomBatchQuery(train_dataset,
                                         batch_size=queryParams[0],
                                         random_state=2311 \
                                         if fixRandomState else None) 

    elif queryStrategyID==4:
        queryStrategy = LeastCertainBatchQuery(train_dataset,
                                               model=queryParams[0],
                                               batch_size=queryParams[1],
                                               random_state=2317 \
                                               if fixRandomState else None)

    elif queryStrategyID==5:
        queryStrategy = SemiSupervisedBatchQuery(train_dataset,
                                                 model=queryParams[0],
                                                 batch_size=queryParams[1],
                                                 random_state=3112 \
                                                 if fixRandomState else None)

    return queryStrategy

