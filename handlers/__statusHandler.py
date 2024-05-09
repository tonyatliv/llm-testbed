import os
import json
import utils
from . import ConfigHandler

class StatusHandler:
    __status = {}
    
    def __init__(self, pmid: str):
        config = ConfigHandler()
        
        self.__pmid = pmid
        self.__filePath = os.path.join(config.getStatusFolderPath(), f"{self.__pmid}.json")
        
        if os.path.isfile(self.__filePath):
            with open(self.__filePath, "r") as file:
                self.__status = json.load(file)
            
    def get(self):
        return self.__status
    
    def update(self, newStatus):
        self.__status = newStatus
        self.__saveStatus()
            
    def __saveStatus(self):
        with open(self.__filePath, "w") as file:
            json.dump(self.__status, file, indent=4)
    
    def getStatusFilePath(self):
        return self.__filePath
    
    def getPMID(self):
        return self.__pmid
    
    def getPDFPath(self):
        if not utils.hasattrdeep(self.__status, ["getPaperPDF", "filename"]):
            raise KeyError("No PDF filename found.")
        
        return os.path.join(ConfigHandler().getPDFsFolderPath(), self.__status['getPaperPDF']['filename'])
    
    def isPDFFetched(self):
        return utils.hasattrdeep(self.__status, ["getPaperPDF", "status"]) and self.__status["getPaperPDF"]["status"] == "fetched"
    
    def isPaperConverted(self):
        return utils.hasattrdeep(self.__status, ["getPlaintext", "status"]) and self.__status["getPlaintext"]["status"] == "converted"    
    
    def getPlaintextFilePath(self):
        if not utils.hasattrdeep(self.__status, ["getPlaintext", "filename"]):
            raise KeyError("No Plaintext filename found.")
        
        return os.path.join(ConfigHandler().getPlaintextFolderPath(), self.__status['getPlaintext']['filename'])
            
    def isJSONFetched(self):
        return utils.hasattrdeep(self.__status, ["getPaperJSON", "status"]) and self.__status["getPaperJSON"]["status"] == "fetched"
    
    def getJSONFilePath(self):
        if not utils.hasattrdeep(self.__status, ["getPaperJSON", "filename"]):
            raise KeyError("No JSON filename found.")
        
        return os.path.join(ConfigHandler().getJSONFolderPath(), self.__status['getPaperJSON']['filename'])
    