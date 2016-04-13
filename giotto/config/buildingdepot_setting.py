import json

class BuildingDepotSetting:
    def __init__(self, settingFilePath="./buldingdepot_setting.json"):
        self.setting = json.loads(open(settingFilePath,'r').read())

    def get(self, settingName):
        return self.setting[settingName]
