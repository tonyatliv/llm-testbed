import json 
import os

class ConfigHandler:
    def __init__(self, file=str(os.getenv("LLM_TESTBED_CONFIG_PATH"))):
        self.file = file
        with open(file, "r") as f:
            self.__config = json.load(f)
            
    def getConfig(self):
        return self.__config
            
    def refresh(self):
        with open(self.file, "r") as f:
            self.__config = json.load(f)
            
    def getStatusFolderPath(self):
        return self.__config["paths"]["status"]
    
    def getPDFsFolderPath(self):
        return self.__config["paths"]["pdf"]
    
    def getPlaintextFolderPath(self):
        return self.__config["paths"]["plaintext"]
    
    def getJSONFolderPath(self):
        return self.__config["paths"]["sections"]
    
    def getMergeSectionsSections(self):
        return self.__config["getTextFromJSON"]["sections"]
    
    def getSystemPromptForGetPaperSpecies(self):
        return self.__config["getPaperSpecies"]["systemPrompt"]
    
    def getResponseSchemaForGetPaperSepcies(self):
        return self.__config["getPaperSpecies"]["responseSchema"]