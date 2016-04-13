"""Machine learning sample class for the machine learning layer"""
import json

class MLSample:
    def __init__(self, dictionary=None):
        '''Initializes an instance

        Initializes an instance with 0, null, and None when dictionary is not passed.
        When a dictionary is passed, sets properties based on the dictionary. To
        obtain timeseries data for this sample, the system retrieves virtual sensor
        information using sensor_id. The information contains an array of real sensors
        related to the virtual sensor. Then, the system pass the array, start_time, and
        end_time to fucntions in datbase.manager to obtain timesereis data.

        Args:
            dictionary: a dictionary that contains properties.
                {
                    '_id': An object ID of a sample
                    'user_id': A user ID of an owner of this sample
                    'label': A user defined label for this sample
                    'start_time': A unix timestamp when the sample starts
                    'end_time': A unix timestamp when the sample ends
                    'sensor_id': An object ID of a virtual sensor to which this sample
                        is related. 
                }

        Returns: A MLSample instance
        '''
        if dictionary == None:
            self.user_id = ''
            self.label = ''
            self.start_time = 0
            self.end_time = 0
            self.object_id = ''
            self.sensor_id = ''
        else:
            self.user_id = dictionary['user_id']
            self.label = dictionary['label']
            self.start_time = dictionary['start_time']
            self.end_time = dictionary['end_time']
            self.object_id = str(dictionary['_id'])
            self.sensor_id = dictionary['sensor_id']

    def to_json(self):
        '''Returns a JSON representation of a MLSample instance'''
        return json.dumps(self, default=lambda o: o.__dict__, separators=(',',':'))

    def to_dictionary(self):
        '''Returns a dictionary representation of a MLSample instance''' 
        data = {
            "user_id": self.user_id,
            "sample_id":self.object_id,
            "start_time":self.start_time,
            "end_time": self.end_time,
            "sensor_id": self.sensor_id,
            "label":self.label
        }

        return data

