import json
import pickle
import numpy as np

class MLClassifier:
    '''Classifier base class'''
    def __init__(self, dictionary=None, serialized=False):
        '''Initializes an instance

        Initializes an instance with 0, null, and None when dictionary is not passed.
        When a dictionary is passed, sets properties based on the dictionary. If the
        dictionary is fetched from a database, classifier, scaler, model, and selector
        are serialized. Thus, loads them before setting.

        Args:
            dictionary: a dictionary that contains properties.
                {
                    '_id': An object ID of a classifier
                    'sensor_id': An object ID of a virtual sensor which this classifier
                        is associated to
                    'user_id': A user ID of an owner of this classifier
                    'model_name':'random forest'
                    'labels': a list of potential outputs from this classifier
                    'sampling_period': A length of timeseries data necessary to make
                        a prediction. This value is calculated when this classifier is
                        trained by taking average of sampling periods of all samples
                        in a given training set
                    'classifier': A trained random forest classifier
                    'scaler': A scaler that scales inputs as a part of pre-processing
                    'selector': A feature selector
                }

        Returns: A MLClassifier instance
        '''

        if dictionary == None:
            self.object_id = ''
            self.sensor_id = ''
            self.model_name = ''
            self.user_id = ''
            self.model = None
            self.classifier = None
            self.scaler = None
            self.selector = None
            self.labels = []
            self.sampling_period = 0
        else:
            self.object_id = str(dictionary['_id'])
            self.sensor_id = dictionary['sensor_id']
            self.user_id = dictionary['user_id']
            self.model_name = dictionary['model_name']
            self.labels = dictionary['labels']
            self.sampling_period = dictionary['sampling_period']

            if serialized:
                self.classifier = pickle.loads(dictionary['classifier'])
                self.scaler = pickle.loads(dictionary['scaler'])
                self.model = pickle.loads(dictionary['model'])
                self.selector = pickle.loads(dictionary['selector'])
            else:
                self.classifier = dictionary['classifier']
                self.scaler = dictionary['scaler']
                self.model = dictionary['model']
                self.selector = dictionary['selector']

    def to_dictionary(self, serialized=False):
        '''Creates a dictionary that contains all properties

        Creates a dictionary that contains all properties to store a classifier
        in a database. When serialized=True, classifier, scaler, selector, and
        model instance are serialized.

        Args:
            serialized: A flag that indicates if instances should be serialized or not

        Returns:
            dic: A dictionary that contains all properties, typically used to store
                a classifier in a database 
        '''
        dic = {
            'object_id': self.object_id,
            'sensor_id': self.sensor_id,
            'user_id': self.user_id,
            'model_name': self.model_name,
            'sampling_period': self.sampling_period,
            'labels': self.labels
        }

        if serialized:
            dic['classifier'] = pickle.dumps(self.classifier)
            dic['scaler'] = pickle.dumps(self.scaler)
            dic['selector'] = pickle.dumps(self.selector)
            dic['model'] = pickle.dumps(self.model)
        else:
            dic['classifier'] = self.classifier
            dic['scaler'] = self.scaler
            dic['selector'] = self.selector
            dic['model'] = self.model

        return dic

    def train(self, dataset):
        '''Trains a classifier using the dataset as a training set

        A derived class should implement a training algorithm that creates and
        train classifier, scaler, selector, and model here. 

        Args:
            dataset: A dictionary that holds a training set
                {
                    'data': An array of training samples
                         [
                            {
                                'timeseries': An array of timeseries data arrays
                                'label': A string label for the timeseries data
                            },
                            { more samples }
                        ]
                    'labels': An array of string labels
                    'sampling_period': An average duration of samples
                }

        Returns:
            Nothing 
        '''
        pass

    def predict(self, timeseries):
        '''Makes a prediction using a pre-trained classifier

        A derived class should implement a prediction algorithm here.
        
        Args: 
            timeseries: Timeseries data for prediction

        Returns:
            label: a string label as a prediction
        '''
        pass

    def to_json(self):
        '''Returns a JSON representation of a MLClassifier instance'''
        return json.dumps(self, default=lambda o: o.__dict__, separators=(',',':'))

    def preprocess(self, sensor_readings):
        '''Extracts features from timeseries data

        Extracts the following features from a array of timeseries data.
        Averages, standard deviations, numbers of peaks, medians, minimum values,
        maximum values, numbers of zero-crossing, differences between max and min.
        If you want to implement your own feature extraction, overwrite this function
        in a derived class.

        Args:
            sensor_readings: An array of timeseries data

        Returns:
            f: a ndarray that contains features for each timeseries data 
        '''
        colNum = len(sensor_readings)
        features = np.zeros((colNum,8))

        for col in range(0,colNum):

            vals = np.array(sensor_readings[col]).astype('float')
            # average
            features[col,0] = np.average(vals)
            
            # std
            features[col,1] = np.std(vals)
            
            # peak count
            features[col,2] = self.peak_count(vals)

            # median
            features[col,3] = np.median(vals)

            # min
            features[col,4] = np.min(vals)

            # max
            features[col,5] = np.max(vals)

            # zero crossing
            features[col,6] = self.zero_crossing(vals)

            # max - min
            features[col,7] = features[col-1,5] - features[col-1,4]

        f = features.reshape(1,colNum*8)[0]

        return f

    def zero_crossing(self, data):
        '''Counts the number of zero-crossing in given timesries data'''
        count = 0
        for idx in range(len(data)-1):
            if data[idx]*data[idx+1] < 0:
                count = count + 1

        return count

    def peak_count(self, data):
        '''Counts the number of peaks in given timesries data'''
        count = 0
        std = np.std(data)
        for idx in range(len(data)-2):
            if data[idx+1] > std*2 and (data[idx+1] - data[idx]) * (data[idx+2] - data[idx+1]) < 0:
                count = count + 1

        return count


