import requests
import time
import json
import time
import calendar
from giotto.config.buildingdepot_setting import BuildingDepotSetting 

class BuildingDepotHelper:
    def __init__(self, settingFilePath="../config/buildingdepot_setting.json"):
        setting = BuildingDepotSetting(settingFilePath)
        self.bd_rest_api = setting.get('buildingdepot_rest_api')
        self.oauth = setting.get('oauth')
        self.access_token = self.get_oauth_token()

    def get_oauth_token(self):
        headers = {'content-type': 'application/json'}
        url = self.bd_rest_api['server']
        url += ':' + self.bd_rest_api['port'] 
        url += '/oauth/access_token/client_id='
        url += self.oauth['id']
        url += '/client_secret='
        url += self.oauth['key']
        result = requests.get(url, headers=headers)

        if result.status_code == 200:
            dic = result.json()
            return dic['access_token']
        else:
            return ''

    def get_timeseries_data(self, uuid, start_time, end_time):
        headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
            }
        url = self.bd_rest_api['server']
        url += ':' + self.bd_rest_api['port'] 
        url += self.bd_rest_api['api_prefix'] + '/sensor/'
        url += uuid + '/timeseries?'
        url += 'start_time=' + str(start_time)
        url += '&end_time=' + str(end_time)

        result = requests.get(url, headers=headers)
        json = result.json()

        readings = json['data']['series'][0]
        columns = readings['columns']
        values = readings['values']
        index = columns.index('value')

        data = []
        for value in values:
            data.append(value[index])

        return data

if __name__ == "__main__":
    bd_helper = BuildingDepotHelper()
    result = bd_helper.get_timeseries_data('75b0d00c-c8c3-4a76-9876-63809fe926c8', 1459971953, 1459971960)


    