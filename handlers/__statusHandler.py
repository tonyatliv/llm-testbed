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
        if not utils.hasattrdeep(self.__status, ["downloadPaper", "filename"]):
            raise KeyError("No PDF name found.")
        
        return os.path.join(ConfigHandler().getPDFsFolderPath(), self.__status['downloadPaper']['filename'])
    
    def isPaperDownloaded(self):
        return utils.hasattrdeep(self.__status, ["downloadPaper", "status"]) and self.__status["downloadPaper"]["status"] == "downloaded"
    
    def isPaperConverted(self):
        return utils.hasattrdeep(self.__status, ["convertPDF", "status"]) and self.__status["convertPDF"]["status"] == "converted"    
            
    def areSectionsFetched(self):
        return utils.hasattrdeep(self.__status, ["getSectionsJSON", "status"]) and self.__status["getSectionsJSON"]["status"] == "fetched"
    
    def getSectionsFilePath(self):
        if not utils.hasattrdeep(self.__status, ["getSectionsJSON", "filename"]):
            raise KeyError("No PDF name found.")
        
        return os.path.join(ConfigHandler().getSectionsFolderPath(), self.__status['getSectionsJSON']['filename'])