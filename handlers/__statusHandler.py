import os
import json
import utils
import handlers

class StatusHandler:
    def __init__(self, pubMedID: str):
        config = handlers.ConfigHandler()
        
        self.__pubMedID = pubMedID
        self.__filePath = os.path.join(config.getStatusFolderPath(), f"{id}.json")
        
        if not os.path.isfile(self.__filePath):
            self.status = {}
            self.__saveStatus()
            return
        
        with open(self.__filePath, "r") as file:
            self.status = json.load(file)
            
    def get(self):
        return self.status
    
    def getFilePath(self):
        return self.__filePath
    
    def getPubMedID(self):
        return self.__pubMedID
    
    def isPaperDownloaded(self):
        return utils.hasattrdeep(self.status, ["downloadPaper", "status"]) and self.status["downloadPaper"]["status"] == "downloaded"
    
    def isConvertedToPlaintext(self):
        return utils.hasattrdeep(self.status, ["convertPDF", "status"]) and self.status["convertPDF"]["status"] == "converted"    
    
    def set(self, newStatus):
        self.status = newStatus
        self.__saveStatus()
            
    def __saveStatus(self):
        with open(self.__filePath, "w") as file:
            json.dump(file, self.status, indent=4)
            