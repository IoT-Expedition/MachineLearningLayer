import giotto.ml.database.manager as db_manager
from giotto.ml.database.sensor import MLSensor
from giotto.ml.database.classifier import MLClassifier

import time
from datetime import timedelta

class MLClassifierResult:
    '''A container class to hold results from giotto.ml.classifier.manager module'''
    def __init__(self):
        self.result = "ok"
        self.message = ''
        self.value = None

def train(sensor_id, user_id):
    '''Trains a classifier for a virtual sensor

    Trains a classifier for a virtual sensor using its samples as a training set.
    A trained classifier is stored in a database and can be used to make predictions.
    This function generated a training set based on timestamps and labels obtained
    from samples. Then, pass the training set to classifier.train.
    Actual feature extraction and training are implemented in a classifier class.
    Check random_forest.py for current the implementation of the current classifier. 

    Args:
        sensor_id: An object ID of a virtual sensor
        user_id: A user ID of a user who own this virtual sensor

    Returns:
        cls_result: An instance of a container class MLClassifierResult
    '''
    clf_result = MLClassifierResult()

    # Load classifier. If no classifier is stored, create a new one
    classifier = db_manager.classifier(sensor_id, user_id)
    if classifier is None:
        classifier = MLRandomForest()
        classifier.sensor_id = sensor_id
        classifier.user_id = user_id

    # Load a training set from a database
    dataset = db_manager.dataset(sensor_id, user_id)
    if dataset is None:
        clf_result.result = 'error'
        clf_result.message = 'No samples in a training set'
        return clf_result

    # Train a classifier and store it in a database
    classifier.train(dataset)
    result = db_manager.store_classifier(classifier)
    if result is None:
        clf_result.result = 'error'
        clf_result.message = 'Could not store a classifier in database'
        return clf_result            

    return clf_result

def predict(sensor_id, user_id, end_time=None):    
    '''Makes a prediction with a virtual sensor

    Makes a prediciton using a pre-trained classifer with timeseries data in a range
    [end time - sampling period, end time]. sampling period is an average of sampling
    durations in a traing set, which is stored as a part of a classifier.
    When end_time is not specifiec, current time is used as end_time.
    This function generated a sample on timestamps passed to this function. Then,
    makes a prediction using a pre-trained classifier.
    Actual feature extraction and prediction are implemented in a classifier class.
    Check random_forest.py for current the implementation of the current classifier. 

    Args:
        sensor_id: An object ID of a virtual sensor.
        user_id: A user ID of a user who own the virtual sensor. 

    Returns:
        cls_result: An instance of a container class MLClassifierResult
    '''    
    clf_result = MLClassifierResult()
    classifier = db_manager.classifier(sensor_id, user_id)

    if classifier is None:  # classifier not found in the database
        clf_result.result = 'error'
        clf_result.message = 'A classifier for the sensor not found.'
        return clf_result

    sensor = db_manager.sensor(sensor_id, user_id)

    if end_time is not None:
        end_time = float(end_time)
        timeseries = db_manager.timeseries_for_inputs(sensor.inputs, end_time-classifier.sampling_period, end_time)
    else:
        timeseries = db_manager.latest_timeseries_for_inputs(sensor.inputs, classifier.sampling_period)

    prediction = classifier.predict(timeseries)   # make prediction

    if prediction is None:  # cannot make a prediction
        clf_result.result = 'error'
        clf_result.message = 'A classification error occurred.'
        return clf_result

    clf_result.prediction = prediction
    print prediction

    return clf_result

if __name__=="__main__":
    # code for a quick test
    result = train('56d39911a9705e0c2b966d6a','default')

    print result