'''Randome Forest Classifer Module'''

from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import cross_val_score
from sklearn import preprocessing
from sklearn import feature_selection

import pickle
import numpy as np

from giotto.ml.database.classifier import MLClassifier
from giotto.ml.database.sensor import MLSensor  


class MLRandomForest(MLClassifier):
    '''Random Forest classifier class

    This class train a Random Forest classifier using a dataset passed to the
    train function. Then, it makes a prediction using timeseries data given to
    the "predict" function. 
    If you want to implement a classifier class using other models, replicate
    this class. The class have to implement two functions at least, train and predict.
    '''
    def __init__(self, dictionary=None, serialized=False):
        MLClassifier.__init__(self, dictionary, serialized)
        if self.model is None:
            self.model = RandomForestClassifier()
            self.model_name = 'random forest'

    def extract_features(self, dataset):
        '''Extracts features from a given dataset

        Extracts features with the preprocess function. The function is implemented
        in the MLClassifier class.
        '''
        data = dataset['data']
        labels = dataset['labels']

        all_features = []
        all_labels = []

        for sample in data:
            raw_data = sample['timeseries']

            features = self.preprocess(raw_data)
            indexed_label = labels.index(sample['label'])

            # Stack features and labels
            if all_features == []:
                all_features = features
            else:
                all_features = np.vstack((all_features,features))

            all_labels.append(indexed_label)

        data = {
            'features':all_features,
            'labels':all_labels,
            'sampling_period':dataset['sampling_period']
        }

        return data            

    def train(self, dataset):
        '''Trains a random forest classifier'''

        # Generate a training set
        data = self.extract_features(dataset)

        # Prescale
        self.scaler = preprocessing.StandardScaler().fit(data['features'])
        scaledFeatures = self.scaler.transform(data['features'])

        # Select features  Random Forest does not require feature selection
        # For other classifier uncomment the next 2 lines and do feature selection
        #self.selector = feature_selection.SelectKBest(feature_selection.f_regression).fit(scaledFeatures, data.labels)
        #selectedFeatures = self.selector.transform(scaledFeatures)

        # Train a classifier
        self.classifier = self.model.fit(scaledFeatures, data['labels'])
        self.sampling_period = data['sampling_period']
        self.labels = dataset['labels']

    def predict(self, timeseries):
        '''Makes a prediction using a pre-trained random forest classifier'''

        features = self.preprocess(timeseries)
        features = features.reshape(1, -1)

        # prescaling
        scaled_features = self.scaler.transform(features)

        # Feture selection
        #selectedFeatures = selector.transform(scaledFeatures)

        # Prediction
        predictions = self.classifier.predict(scaled_features)

        return self.labels[predictions[0].astype(int)]

if __name__=="__main__":
    clf = MLRandomForest('56b3c0f023cf8c29e049e89e','default')

    clf.train()












