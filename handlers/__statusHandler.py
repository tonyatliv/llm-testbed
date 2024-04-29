import os
import json
import utils
from . import ConfigHandler

class StatusHandler:
    __status = {}
    
    def __init__(self, pubMedID: str):
        config = ConfigHandler()
        
        self.__pubMedID = pubMedID
        self.__filePath = os.path.join(config.getStatusFolderPath(), f"{self.__pubMedID}.json")
        
        if os.path.isfile(self.__filePath):
            with open(self.__filePath, "r") as file:
                self.__status = json.load(file)
            
    def get(self):
        return self.__status
    
    def getStatusFilePath(self):
        return self.__filePath
    
    def getPubMedID(self):
        return self.__pubMedID
    
    def getPDFPath(self):
        if not utils.hasattrdeep(self.__status, ["downloadPaper", "filename"]):
            raise KeyError("No PDF name found.")
        
        return os.path.join(ConfigHandler().getPDFsFolderPath(), f"{self.__status['downloadPaper']['filename']}")
    
    def isPaperDownloaded(self):
        return utils.hasattrdeep(self.__status, ["downloadPaper", "status"]) and self.__status["downloadPaper"]["status"] == "downloaded"
    
    def isPaperConverted(self):
        return utils.hasattrdeep(self.__status, ["convertPDF", "status"]) and self.__status["convertPDF"]["status"] == "converted"    
    
    def update(self, newStatus):
        self.__status = newStatus
        self.__saveStatus()
            
    def __saveStatus(self):
        with open(self.__filePath, "w") as file:
            json.dump(self.__status, file, indent=4)
            