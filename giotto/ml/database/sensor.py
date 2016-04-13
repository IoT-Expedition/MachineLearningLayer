"""Machine learning sensor class for the machine learning layer"""
import json

class MLSensor:
    def __init__(self, dictionary=None):
        if dictionary == None:
            self.name = ''
            self.user_id = ''
            self.labels = []
            self.inputs = []
            self.object_id = ''
            self.sensor_uuid = ''
            self.description = ''
        else:
            self.name = dictionary['name']
            self.user_id = dictionary['user_id']
            self.labels = dictionary['labels']
            self.inputs = dictionary['inputs']
            self.sensor_uuid = dictionary['sensor_uuid']
            self.description = dictionary['description']
            if '_id' in dictionary:
                self._id = str(dictionary['_id'])
            else:
                self._id = None

    def to_json(self):
        '''Returns a JSON representation of a MLSensor instance'''
        return json.dumps(self, default=lambda o: o.__dict__, separators=(',',':'))

    def to_dictionary(self):
        '''Returns a dictionary representation of a MLSensor instance''' 
        data = {
            "name": self.name,
            "sensor_uuid":self.sensor_uuid,
            "user_id": self.user_id,
            "labels": self.labels,
            "inputs": self.inputs,
            "description": self.description
        }
        
        if self._id is not None:
            data['_id'] = self._id

        return data

