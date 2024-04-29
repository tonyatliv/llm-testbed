import os
import config
import json

class StatusHandler:
    def __init__(self, pubMedID: str):
        self.pubMedID = pubMedID
        self.filePath = os.path.join(config.getStatusFolderPath(), f"{id}.json")
        
        if not os.path.isfile(self.filePath):
            self.status = {}
            self.__saveStatus()
            return
        
        with open(self.filePath, "r") as file:
            self.status = json.load(file)
            
    def get(self):
        return self.status
    
    def set(self, newStatus):
        self.status = newStatus
        self.__saveStatus()
            
    def __saveStatus(self):
        with open(self.filePath, "w") as file:
            json.dump(file, self.status, indent=4)
            