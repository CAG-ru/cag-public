import json

class ConfigParser:
    
    def __init__(self, configPath):
        with open(configPath, 'r') as fp:
            self.configParameters = json.load(fp)

    def available_extensions(self):
        return list(self.configParameters.keys())

    def get_config_by_extention(self, ext):
        return self.configParameters.get(ext)
    
    def __str__(self):
        return str(self.configParameters)