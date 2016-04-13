"""A data management module

Handles database manipulattion related to the machine learning layer.
Timeseries data is stored in InfluxDB and other data is stored in MongoDB. 
""" 

import sys
import pickle
import json
import pymongo
import time
import datetime
from pymongo import MongoClient
from influxdb import InfluxDBClient

from bson.objectid import ObjectId
from giotto.ml.database.sensor import MLSensor
from giotto.ml.database.sample import MLSample
from giotto.ml.database.classifier import MLClassifier
from giotto.ml.classifier.random_forest import MLRandomForest
from giotto.helper.buildingdepot_helper import BuildingDepotHelper

mongo_client = MongoClient().machine_learning
influx_client = InfluxDBClient('localhost', 8086, 'root', 'root', 'buildingdepot')
buildingdepot_helper = BuildingDepotHelper('../../config/buildingdepot_setting.json')

def insert_sensor(sensor):
    '''Inserts a sensor entry to MongoDB

    Args:
        sensor: MLSensor instance that holds sensor information.

    Returns:
        An object ID of the inserted sensor entry or None if insertion failed.
    '''
    dic = sensor.to_dictionary()
    result = mongo_client.sensors.insert_one(dic)
    
    return str(result.inserted_id)

def update_sensor(sensor):
    '''Updates an existing sensor entry in MongoDB

    Args:
        sensor: MLSensor instance that holds sensor information

    Returns:
        An object ID of the updated sensor entry
    ''' 
    col = mongo_client.sensors
    dic = sensor.to_dictionary()
    del dic['_id']
    result = col.update_one({'_id':ObjectId(sensor._id)}, {'$set':dic})

    return sensor._id

def delete_sensor(sensor_id, user_id):
    '''Deletes an existing sensor entry in MongoDB

    Args:
        sensor_id: An object ID of a sensor to be deleted
        user_id: A user ID of a user who perform this manipulation
    '''
    mongo_client.sensors.delete_one({'_id':ObjectId(sensor_id)})

def sensor(sensor_id, user_id):
    '''Get sensor informaiton

    Args:
        sensor_id: An object ID of a sensor to be deleted
        user_id: A user ID of a user who perform this manipulation

    Returns:
        sensor: A MLSensor instance or None if there is no sensor with
            a given sensor_id        
    '''
    result = mongo_client.sensors.find({'_id':ObjectId(sensor_id)})
    if result.count != 0:
        sensor = MLSensor(result[0])
        return sensor
    else:
        return None

def sensors(user_id):
    '''Get a list of sensors that a user owns

    Args:
        user_id: A user ID of a user.

    Retuens:
        An array of MLSensor instances
    '''
    result = mongo_client.sensors.find({'user_id':user_id})
    sensors = []
    for row in result:
        sensor = MLSensor(row)
        sensors.append(sensor.to_dictionary())

    return sensors

def insert_sample(sensor_id, user_id, start_time, end_time, label):
    '''Inserts a training sample

    Inserts a training sample that will be used to train a machine learning
    classifier later.

    Args:
        sensor_id: An object ID of a virtual sensor related to a` training sample
        user_id: A user ID of a user who perform this manipulation
        start_time: A unix timestamp when a sample starts
        end_time: A unix timestamp when a sample ends
        label: A string label for a sample

    Returns:
        An object ID of an inserted sample or None if insertion fails
    '''
    sample = {
        'sensor_id':sensor_id,
        'user_id':user_id,
        'start_time':start_time,
        'end_time':end_time,
        'label':label
    }
    result = mongo_client.samples.insert_one(sample)

    return str(result.inserted_id)

def delete_sample(sensor_id, user_id, sample_id):
    '''Deletes a sample

    Args:
        sensor_id: An object ID of a virutal sensor
        user_id: A user ID of a user who perform deletion
        sample_id: An object ID of a sample to be deleted

    Return:
        1 if deletion was successful, or 0 otherwise
    '''
    condition = {
        '_id':ObjectId(sample_id),
        'sensor_id':sensor_id,
        'user_id':user_id
    }
    result = mongo_client.sensors.delete_one(condition)

    return result.deleted_count

def delete_all_samples(sensor_id, user_id):
    '''Deletes all samples

    Args:
        sensor_id: An object ID of a virutal sensor
        user_id: A user ID of a user who perform deletion
        sample_id: An object ID of a sample to be deleted

    Return:
        1 if deletion was successful, or 0 otherwise
    '''

    condition = {
        'sensor_id':sensor_id,
        'user_id':user_id
    }
    result = mongo_client.sensors.delete_many(condition)

    return result.deleted_count

def samples(sensor_id, user_id):
    '''Gets a list of samples

    Gets an array consisting of MLSample instances related to a specified virtual sensor.

    Args:
        sensor_id: An object ID of a virtual sensor
        user_id: A user ID of a user who perform this

    Returns:
        An array consisting of MLSample instances
    '''

    result = mongo_client.samples.find({'user_id':user_id, 'sensor_id':sensor_id})
    samples = []
    for row in result:
        sample = MLSample(row)
        samples.append(sample)

    return samples

def sample(sample_id, user_id):
    '''Gets a sample

    Gets a MLSample instances related to a specified virtual sensor.

    Args:
        sensor_id: An object ID of a virtual sensor
        user_id: A user ID of a user who perform this

    Returns:
        A MLSample instance or None if a sample with specified object ID not found
    '''
    result = mongo_client.samples.find({'_id':ObjectId(sample_id)})
    if result.count != 0:
        sample = MLSample(result[0])
        return sample
    else:
        return None

def store_classifier(classifier):
    '''Stores a classifier in MongoDB

    Stores a MLClassifier instance (or an instance of its derived class) in MongoDB
    When the classifier already exist in the database (i.e., if its object ID has
    a valid value), this function update the existing entry, otherwise, it inserts
    a new entry.

    Args:
        classifier: A MLClassifier instance

    Returns:
        An object ID of an entry that stores the instance, or None if the operation
        fails
    '''
    if classifier.object_id is None or classifier.object_id == '':
        object_id = insert_classifier(classifier)
    else:
        object_id = update_classifier(classifier)

    return object_id

def insert_classifier(classifier):
    '''Inserts a classifier in MongoDB

    Args:
        classifier: A MLClassifier instance

    Returns:
        An object ID of an inserted entry, or None if the operation fails
    '''
    clf = classifier.to_dictionary(True)
    result = mongo_client.classifiers.insert_one(clf)

    return str(result.inserted_id)


def update_classifier(classifier):
    '''Updates a classifier in MongoDB

    Args:
        classifier: A MLClassifier instance

    Returns:
        An object ID of an updated instance, or None if the operation fails
    '''
    if classifier.object_id is None or classifier.object_id == '':
        return None

    object_id = ObjectId(classifier.object_id) 
    updated_doc = mongo_client.classifiers.update({'_id':object_id}, classifier.to_dictionary(serialized=True))

    if updated_doc is None or updated_doc['err'] is not None:
        return None
    else:
        return object_id


def classifier(sensor_id, user_id, model='random forest'):
    '''Gets a classifier

    Gets a classifier instance related to a specified virtual sensor. If no classifier
    exists for the virutal sensor, this function creates a new instance and return it.
    This implementation use random forest. If you want to add other classifiers
    with other models, modify code in this function.

    Args:
        sensor_id: An object ID of a virtual sensor
        user_id: A user ID of a user who perform this operation
        model: A name of a machine learning model used for this classifier

    Returns:
        MLClassifier (or its delived class) instance
    '''
    result = mongo_client.classifiers.find({'user_id':user_id, 'sensor_id':sensor_id})

    if result.count() > 0:
        dic = result[0]
        clf = MLRandomForest(dic, serialized=True)
    else:
        clf = MLRandomForest()
        clf.sensor_id = sensor_id
        clf.user_id = user_id

    return clf

def delete_classifier(classifier, user_id):
    '''Delets a classifier'''

    result = mongo_client.classifier.remove({'_id':ObjectId(classifier)})

def dataset(sensor_id, user_id):
    '''Returns a training set for a virtual sensor

    Returns a training set for a virutla sensor. The training set consisting of samples,
    an array of labels, and a sampling priod. A sample consists of an array of timeseries
    data and a label. The timeseries data is extracted from InfluxDB based on MLSamples
    instances stored in MongoDB.

    Args:
        sensor_id: An object ID of a virutal sensor
        user_id: A user ID of a user who perfrom this operation

    Returns: A dictionary consisting of:
        {
            'data':[
                {
                    'timeseries': An array of timeseries data from real sensors
                    'lable': A label for a sample
                },
                { more samples }
            ]
            'sampling_period': An average sampling period in seconds.
                The sampling_period when making a prediction is deciced by this value
            'label': An array of labels (i.e., potential predictions)
        }
    '''
    data = []
    labels = []
    sampling_period_sum = 0

    smpls = samples(sensor_id, user_id)

    if len(smpls) == 0:
        return None

    for sample in smpls:
        sampling_period_sum = sampling_period_sum + sample.end_time - sample.start_time

        raw_data = timeseries_for_sample(sample.object_id, user_id)

        if sample.label not in labels:
            labels.append(sample.label)
        
        data.append({'timeseries':raw_data, 'label':sample.label})

    dataset = {'data':data, 'sampling_period':sampling_period_sum/len(data), 'labels':labels}

    return dataset

def timeseries_for_sample(sample_id, user_id):
    '''Returns timeseries data for a given sample

    Returns an array of timeseries data for a given sample. The sample has start_time,
    end_time, and sensor_id for a virutal sensor. A virtual sensor has an array of
    real sensors related to that virtual sensor. This function extracts timeseries data
    of these real sensors between start_time and end_time.

    Args:
        sample_id: An object ID of a sample
        user_id: A user ID of a user who perform this operaiton

    Returns:
        An array of timeseris data from multiple real sensors. Note that the lenghts
        of real time data vary among the real sensors because of their differences in
        sampling rates. Thus the return value is one-dimensional array of
        one-dimensional arrays, not a two-dimensional array.
    '''
    result = mongo_client.samples.find({'_id':ObjectId(sample_id)})
    if result.count != 0:
        sample = MLSample(result[0])
    else:
        return []

    snsr = sensor(sample.sensor_id, user_id)
    samples = timeseries_for_inputs(snsr.inputs, sample.start_time, sample.end_time)

    return samples

def timeseries_for_inputs(input_uuids, start_time, end_time):
    '''Returns timeseries data for given real sensors

    Returns an array of timeseries data for real sensors between start_time and
    end_time.

    Args:
        sample_id: An object ID of a sample
        user_id: A user ID of a user who perform this operaiton

    Returns:
        An array of timeseris data from multiple real sensors. Note that the lenghts
        of real time data vary among the real sensors because of their differences in
        sampling rates. Thus the return value is one-dimensional array of
        one-dimensional arrays, not a two-dimensional array.
    '''
    samples = []

    for uuid in input_uuids:
        values = buildingdepot_helper.get_timeseries_data(uuid, start_time, end_time)
        samples.append(values)
        
    return samples
      

def latest_timeseries_for_inputs(input_uuids, seconds):
    '''Returns timeseries data for given real sensors in the last specified seconds

    Returns an array of timeseries data for real sensors specified by input_uuids
    in the last specified seconds.

    Args:
        input_uuids: An array of real sensors' UUIDs
        seconds: A duration of sampling in seconds

    Returns:
        An array of timeseris data from multiple real sensors. Note that the lenghts
        of real time data vary among the real sensors because of their differences in
        sampling rates. Thus the return value is one-dimensional array of
        one-dimensional arrays, not a two-dimensional array.
    '''
    current_time = time.time()
    time.sleep(2+seconds)

    return timeseries_for_inputs(input_uuids, current_time, current_time+seconds)


def timestamp_to_time_string(t):
    '''Converts a unix timestamp to a string representation of the timestamp

    Args:
        t: A unix timestamp float

    Returns
        A string representation of the timestamp
    '''
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(t)) + str(t-int(t))[1:10]+ 'Z'


def time_string_to_timestamp(string):
    '''Converts a string representation of a timestamp to a unix timestamp

    Args:
        string: A string representation of a timestamp

    Returns
        A unix timestamp
    '''
    s = string[0:19] # Year to second
    t = time.mktime(datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S").timetuple())

    millisec = string[19:-1]    #millisecond
    if millisec[0] == '.':
        millisec = '0' + millisec
        t += float(millisec)

    return t


if __name__=="__main__":
    bd_helper = BuildingDepotHelper()
