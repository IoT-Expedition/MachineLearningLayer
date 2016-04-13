'''
This module implements REST APIs for the GIoTTO machine learning layer
'''
from flask import Flask
from flask import request
from pymongo import MongoClient
from influxdb import InfluxDBClient
import json
import time
from datetime import timedelta
from flask import make_response, current_app
from functools import update_wrapper

import giotto.ml.database.manager as database_manager
import giotto.ml.classifier.manager as classifier_manager

from giotto.ml.database.sensor import MLSensor
from giotto.ml.database.classifier import MLClassifier
from giotto.ml.classifier.manager import MLClassifierResult
from giotto.config.buildingdepot_setting import BuildingDepotSetting 


app = Flask(__name__)


def jsonString(obj,pretty=False):
    if pretty == True:
        return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': ')) + '\n'
    else:
        return json.dumps(obj)

@app.route("/")
def message():
    return "Building Depot Flask Server for the GIoTTO Machine Learning Layer"


@app.route('/time', methods=['GET'])
def get_time():
    '''Returns a current unix timestamp

    Returns a server timestamp. The timestamp is used to mark traning samples for
    machine learning. A sample is recorded in Mongo DB using start time, end time, label,
    and related sensor uuids. Because we cannot guarantee that time is sychronized between
    GIoTTO server and other devices. Use this API to obtain unix timestamps for adding
    training samples.

    Returns:
        {
            "url": A URL of the HTTP call
            "method": "GET"
            "result": "ok"
            "ret": A curernt unix timesamp
        }
    '''
    timestamp = time.time()
    dic = {
        'url':request.url,
        'method':request.method,
        'result':'ok',
        'ret':timestamp
    }

    return jsonString(dic)


@app.route('/sensor', methods=['POST'])
def create_sensor():
    '''Creates a virtual sensor

    Creates a virtual sensor using a JSON passed as data, and returns its object ID.

    Args as data:
        {
            "name": name of a virtual sensor
            "user_id": ID of a user who creates this sensor 
            "labels": An array of strings denoting labels
            "inputs": An array of UUIDs of real sensors used as inputs for a classifier
            "sensor_uuid": A sensor UUID of this virtual sensor in BD (can pass blank) 
            "description": A description of this virtual sensor 
        }

    Returns:
        {
            "url": A URL of the HTTP call
            "method": "POST"
            "result": error when insertion failed, otherwise ok
            "ret": The virtual sensor's ID
        }

    '''
    sensor = MLSensor(request.get_json())
    object_id = database_manager.insert_sensor(sensor)
    
    dic = {
        'url':request.url,
        'method':request.method,
        'ret':object_id
    }

    if object_id is not None:
        dic['result'] = 'ok'
    else:
        dic['result'] = 'error'
    
    return jsonString(dic)


@app.route('/sensors/', methods=['GET'])
def getAllSensors():
    '''Returns a list of all virtual sensors.

    Returns a list of all virtual sensors in the ML layer as an array of objects.

    Returns:
        {
            "url": A URL of the HTTP call
            "method": "GET"
            "result": "ok"
            "ret":[
                {
                    "_id": A virtual sensor's object ID
                    "name": A sensor name
                    "sensor_uuid": A UUID of a sensor if it's registerd in BD
                    "user_id": An ID of a user who created this sensor
                    "labels": An array of labels
                    "inputs": An array of sensor UUIDs in BD used as inputs for a classifier
                    "description": A description of a sensor
                },
                { More sensor objects if there are }
            ]
        }
    '''
    # When access control is fully implemented. user_id has to be identified
    # based on OAuth header of a http request. However, it's not implemented yet
    # Thus 'default' is used here
    user_id = 'default'
    
    sensors = database_manager.sensors(user_id)
    result = []
    for sensor in sensors:
        result.append(sensor)

    dic = {
        'url':request.url,
        'method':request.method,
        'result':'ok',
        'ret':result
    }

    return jsonString(dic)


@app.route('/sensor/<sensor_id>', methods=['GET'])
def get_sensor(sensor_id):
    '''Returns informatoin about a virtual sensor

    Returns an object containing information about a virtual sensor.

    Args as a part of URL:
        <sensor_id>: A sensor's object ID.

    Returns:
        {
            "url": A URL of the HTTP call
            "method": "GET"
            "result": ok or error
            "ret":{
                "_id": A virtual sensor's object ID
                "name": A sensor name
                "sensor_uuid": A UUID of a sensor if it's registerd in BD
                "user_id": An ID of a user who created this sensor
                "labels": An array of labels
                "inputs": An array of sensor UUIDs in BD used as inputs for a classifier
                "description": A description of a sensor
            }
        }    
    '''
    user_id = 'default'
    
    sensor = database_manager.sensor(sensor_id, user_id)
    dic = {
        'url':request.url,
        'method':request.method,
    }
    if sensor is not None:
        dic['ret'] = sensor.to_dictionary()
        dic['result'] = 'ok'
    else:
        dic['result'] = 'error'

    return jsonString(dic)


@app.route('/sensor/<sensor_id>', methods=['PUT'])
def update_sensor(sensor_id):
    '''Updates sensor information

    Updates existing virtual sensor information and returns updated information.

    Args as data:
        {
            "_id": Object ID of an existing virtual sensor
            "name": A name of a virtual sensor
            "user_id": ID of a user who creates this sensor 
            "labels": An array of strings denoting labels
            "inputs": An array of UUIDs of real sensors used as inputs for a classifier
            "sensor_uuid": A sensor UUID of this virtual sensor in BD (can pass blank) 
            "description": A description of this virtual sensor 
        }

    Returns:
        {
            "url": A URL of the HTTP call
            "method": "PUT"
            "result": ok or error
            "ret":{
                "_id": A virtual sensor's object ID
                "name": A sensor name
                "sensor_uuid": A UUID of a sensor if it's registered in BD
                "user_id": An ID of a user who created this sensor
                "labels": An array of labels
                "inputs": An array of sensor UUIDs in BD used as inputs for a classifier
                "description": A description of a sensor
            }
        } 
    '''
    user_id = 'default'
    dic = {
        'uri':request.url,
        'method':request.method
    }

    sensor = MLSensor(request.get_json())
    result = database_manager.update_sensor(sensor)

    if result is not None:
        dic['result'] = 'ok'
        dic['ret'] = database_manager.sensor(sensor._id, user_id).to_dictionary()
    else:
        dic['result'] = 'error'

    return jsonString(dic)


@app.route('/sensor/<sensor_id>', methods=['DELETE'])
def delete_sensor(sensor_id):
    '''Deletes a virtual sensor

    Deletes a virtual sensor, corresponding classifier, and samples from ML Layer's database.

    Args as a part of URL:
        <sensor_id>: An object ID of the virtual sensor 

    Returns:
        {
            "url": A URL of the HTTP call
            "method": "DELETE"
            "result": error when deletion failed, otherwise ok
        }
    '''
    dic = {
        'url':request.url,
        'method':request.method,
    }

    user_id = 'default'
    result = database_manager.delete_sensor(sensor_id, user_id)

    #TODO: Have to delete related classifiers and samples

    if result:
        dic['result'] = 'ok'
    else:
        dic['result'] = 'error'
    
    return jsonString(dic)

@app.route('/sensor/<sensor_id>/sample', methods=['POST'])
def insert_sample(sensor_id):
    '''Adds a training sample to a virtual sensor

    Adds a sample consisting of a start time, an end time and a label to a virtual sensor.
    A virtual sensor has "inputs" property, which is a list of UUIDs of real sensors
    related to the virtual sensor. Timeseries data from these real sensors between
    the start time and the end time is used as a training sample with the label.

    Args as a part of URL:
        <sensor_id>: An object ID of a virtual sensor
    
    Args as data
        {
            "start_time": A unix timestamp denoting when a sample starts
            "end_time": A unix timestamp denoting when a sample ends
            "label": A label string
        }

    Returns:
        {
            "url": A URL of the HTTP call
            "method": "POST"
            "result": error when insertion failed, otherwise ok
            "ret": The sample's ID
        }
    '''
    json = request.get_json()

    sample_id = database_manager.insert_sample(sensor_id, 'default', json['start_time'], json['end_time'], json['label'])

    dic = {
        'uri':request.url,
        'method':request.method
    }

    if sample_id is not None:
        dic['result'] = 'ok'
        dic['ret'] = sample_id
    else:
        dic['result'] = 'error'

    return jsonString(dic)

@app.route('/sensor/<sensor_id>/samples', methods=['GET'])
def get_samples(sensor_id):
    '''Returns an array of samples for a virtual sensor

    Args as a part of URL:
        <sensor_id>: An object ID of a virtual sensor

    Returns:
        {
            "url": A URL of the HTTP call
            "method": "GET"
            "result": error when read failed, otherwise ok
            "ret": An array of sample objects
        }
    '''
    user_id = 'default'

    samples = database_manager.samples(sensor_id, user_id)
    dic = {
        'url':request.url,
        'method':request.method,
    }

    if samples is not None:
        dic['result']='ok'
        dic['ret']=samples
    else:
        dic['result']='error'

    return json.dumps(result)

@app.route('/sensor/<sensor_id>/samples', methods=['DELETE'])
def delete_samples(sensor_id):
    '''Delete all samples for a virutal sensor

    Args as a part of URL:
        <sensor_id>: An object ID of a virtual sensor

    Returns:
        {
            "url": A URL of the HTTP call
            "method": "DELETE"
            "result": error when deletion failed, otherwise ok
        }
    '''
    #TODO: Implement this API
    pass

@app.route('/sensor/<sensor_id>/classifier/train', methods=['POST'])
def train(sensor_id):
    '''Trains a classifier for a virtual sensor

    Trains a classifier for a virtual sensor using its samples as a training set.
    A trained classifier is stored in a database and can be used to make predictions. 

    Args as a part of URL:
    <sensor_id>: An object ID of a virtual sensor_id

    Returns:
        {
            "url": A URL of the HTTP call
            "method": "POST"
            "result": Error when training failed, otherwise ok
            "message": A human readable message from classifier.manager.train
        }
    '''
    user_id = 'default'
    classifier_result = classifier_manager.train(sensor_id, user_id)
    dic = {
        'url':request.url,
        'method':request.method,
        'result':classifier_result.result,
        'message':classifier_result.message
    }

    return jsonString(dic)

@app.route('/sensor/<sensor_id>/classifier/predict', methods=['GET'])
def predict(sensor_id):
    '''Makes a prediction using a classifier

    Makes a prediction using a pre-trained classifier with timeseries data in a range
    [end time - sampling period, end time]. sampling period is an average of sampling
    durations in a training set, which is stored as a part of a classifier.
    When end_time is not specific, current time is used as end_time. 

    Args as a part of URL:
    <sensor_id>: An object ID of a virtual sensor_id

    Args as data:
    end_time: A unix timestamp. When omitted, current time is used as end_time.

    Returns:
        {
            "url": A URL of the HTTP call
            "method": "GET"
            "result": Error when prediction failed, otherwise ok
            "message": A human readable message from classifier.manager.train
            "ret": A predicted label
        }
    '''
    user_id = 'default'
    end_time = request.args.get('time')

    clf_result = classifier_manager.predict(sensor_id, user_id, end_time)    
    dic = {
        'url':request.url,
        'method':request.method,
        'result': clf_result.result,
        'message': clf_result.message,
        'ret': clf_result.prediction
    }

    return jsonString(dic) 


if __name__=="__main__":
    app.run(host='0.0.0.0', debug=True)
