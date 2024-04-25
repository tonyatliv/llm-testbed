import json 

def getConfig(configFile="config.json"):
    with open(configFile, "r") as f:
        return json.load(f)
    
def getStatusFolderPath(configFile="config.json"):
    return getConfig(configFile=configFile)["paths"]["status"]

def getPDFsFolderPath(configFile="config.json"):
    return getConfig(configFile=configFile)["paths"]["pdf"]

def getPlaintextFolderPath(configFile="config.json"):
    return getConfig(configFile=configFile)["paths"]["plaintext"]