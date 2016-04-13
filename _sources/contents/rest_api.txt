==========
REST APIs
==========

Virtual Sensors
=================
Virtual sensors are essentially machine learning classifiers.

Create a Virtual Sensor
^^^^^^^^^^^^^^^^^^^^^^^^
Creates a virtual sensor using a JSON passed as data, and returns its object ID.

API

.. code-block:: none

	POST <server>:<port>/sensor

Arguments as data

.. code-block:: none

	{
		"name": name of a virtual sensor
		"user_id": ID of a user who creates this sensor 
		"labels": An array of strings denoting labels
		"inputs": An array of UUIDs of real sensors used as
			inputs for a classifier
		"sensor_uuid": A sensor UUID of this virtual sensor
			in BD (can pass blank) 
		"description": A description of this virtual sensor 
	}

Returns

.. code-block:: none

	{
	    "url": A URL of the HTTP call
	    "method": "POST"
	    "result": error when insertion failed, otherwise ok
	    "ret": The virtual sensor's ID
	}

Get All Virtual Sensors
^^^^^^^^^^^^^^^^^^^^^^^^^
Returns a list of all virtual sensors in the ML layer as an array of objects.

API

.. code-block:: none

	GET <server>:<port>/sensors/

Arguments: None

Returns

.. code-block:: none

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
	            "inputs": An array of sensor UUIDs in BD used as inputs
	            	for a classifier
	            "description": A description of a sensor
	        },
	        { More sensor objects if there are }
	    ]
	}

Get a Virtual Sensor
^^^^^^^^^^^^^^^^^^^^^
Returns an object containing information about a virtual sensor.

API

.. code-block:: none

	GET <server>:<port>/sensor/{sensor id}

Argument as a part of URL

.. code-block:: none

	{sensor id}; A sensor's object ID

Returns

.. code-block:: none

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
            "inputs": An array of sensor UUIDs in BD used as inputs for
            	a classifier
            "description": A description of a sensor
        }
    } 

Update a Virtual Sensor Information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Updates existing virtual sensor information and returns updated information.

.. code-block:: none

	PUT <server>:<port>/sensor/{sensor id}

Argument as a part of URL

.. code-block:: none

	{sensor id}: A virtual sensor's object ID

Argument as data

.. code-block:: none

	{
	    "_id": Object ID of an existing virtual sensor
	    "name": A name of a virtual sensor
	    "user_id": ID of a user who creates this sensor 
	    "labels": An array of strings denoting labels
	    "inputs": An array of UUIDs of real sensors used as
	    	inputs for a classifier
	    "sensor_uuid": A sensor UUID of this virtual sensor
	    	in BD (can pass blank) 
	    "description": A description of this virtual sensor 
	}

Returns

.. code-block:: none

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
            "inputs": An array of sensor UUIDs in BD used as inputs
            	for a classifier
            "description": A description of a sensor
        }
    }

Delete a Virtual Sensor
^^^^^^^^^^^^^^^^^^^^^^^^^
Deletes a virtual sensor, corresponding classifier, and samples from ML Layer's database.

.. code-block:: none

	DELETE <server>:<port>/sensor/{sensor id}

Argument as a part of URL

.. code-block:: none
	
	{sensor id}: A object ID of a virtual sensor

Returns

.. code-block:: none

    {
        "url": A URL of the HTTP call
        "method": "DELETE"
        "result": error when deletion failed, otherwise ok
    }


Samples
============
Samples are training samples given by users.
A sample contains an object ID of a virtual sensor, a start time, an end time and a label.
A virtual sensor has a list of real sensors related to the virtual sensor.
Thus, using these information, a training set can be constructed later to
train a classifier for a virtual sensor.

Add a Sample to a Virtual Sensor

API

.. code-block:: none

	POST <server>:<port>/sensor/{sensor id}/sample

Arguments as a part of URL

.. code-block:: none

	{sensor id}: An object ID of a virtual sensor

Argument as data

.. code-block:: none

    {
        "start_time": A unix timestamp denoting when a sample starts
        "end_time": A unix timestamp denoting when a sample ends
        "label": A label string
    } 

Returns

.. code-block:: none

    {
        "url": A URL of the HTTP call
        "method": "POST"
        "result": error when insertion failed, otherwise ok
        "ret": The sample's ID
    }

Get a List of Samples for a Virtual Sensor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Returns an array of samples for a virtual sensor.

API

.. code-block:: none

	GET <server>:<port>/sensor/{sensor id}/samples

Arguments as a part of URL

.. code-block:: none

	{sensor id}: An object ID of a virtual sensor

Returns

.. code-block:: none

	{
	    "url": A URL of the HTTP call
	    "method": "GET"
	    "result": error when read failed, otherwise ok
	    "ret": An array of sample objects
	}

Delete Samples for a Virtual Sensor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Deletes all samples for a virtual sensor.

Argument as a part of URL

.. code-block:: none

	{sensor id}: An object ID of a virtual sensor

Returns

.. code-block:: none

    {
        "url": A URL of the HTTP call
        "method": "DELETE"
        "result": error when deletion failed, otherwise ok
    }


Classifier
==========================
Train a Classifier using Samples
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Trains a classifier for a virtual sensor using its samples as a training set.
A trained classifier is stored in a database and can be used to make predictions. 

API

.. code-block:: none

	POST <server>:<port>/sensor/{sensor id}/classifier/train

Argument as a part of URL

.. code-block:: none

	{sensor id}: An object ID of a virtual sensor

Returns

.. code-block:: none

	{
	    "url": A URL of the HTTP call
	    "method": "POST"
	    "result": Error when training failed, otherwise ok
	    "message": A human readable message from classifier.manager.train
	}

Makes a Prediction using a Classifier
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Makes a prediction using a pre-trained classifier with timeseries data in a range
[end time - sampling period, end time]. sampling period is an average of sampling
durations in a training set, which is stored as a part of a classifier.
When end_time is not specific, current time is used as end_time. 

API

.. code-block:: none

	GET <server>:<port>/sensor/{sensor id}/classifier/predict

Argument as a part of URL

.. code-block:: none

	{sensor id}: An object ID of a virtual sensor

Returns

.. code-block:: none

    {
        "url": A URL of the HTTP call
        "method": "GET"
        "result": Error when prediction failed, otherwise ok
        "message": A human readable message from classifier.manager.train
        "ret": A predicted label
    }






