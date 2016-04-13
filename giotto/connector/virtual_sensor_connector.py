"""A connector for a virtual sensor script

Makes predictions periodically and send them to BuildingDepot
"""

import time
import math
import random

from json_setting import JsonSetting
from buildingdepot_helper import BuildingDepotHelper

if __name__ == "__main__":
	#Load settings

	connector_setting = JsonSetting('./connector_setting.json')
	bd_helper = BuildingDepotHelper()

	buildingdepot_uuid = connector_setting.get('sensor_uuid')
	virtual_sensor_id = connector_setting.get('virtual_sensor_id')
	sampling_period = connector_setting.get('sampling_period')

	#Make predictions periodically and send them to BD
	while True:
		data_array = []
		timestamp = time.time()
		
		#Make prediction
        url = 'http://localhost:5000/sensor/' + virtual_sensor_id + '/classifier/predict'
        result = requests.get(url)
        prediction = result['ret']
		
		#Send data
		dic = {}
		dic['sensor_id'] = buildingdepot_uuid
		dic['samples'] = [{"time":timestamp,"value":prediction]
		dic['value_type'] = 'string'
		data_array.append(dic)

		result = bd_helper.post_data_array(data_array)
		time.sleep(sampling_period);