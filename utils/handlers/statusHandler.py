import os
import json
import utils.helpers as helpers
from . import ConfigHandler
from typing import List

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
        
    def updateField(self, field: str | List[str], newValue):
        self.__status[field] = newValue if type(field) == str else helpers.traverseDictAndUpdateField(field, newValue, self.__status)
        self.__saveStatus()
            
    def __saveStatus(self):
        with open(self.__filePath, "w") as file:
            json.dump(self.__status, file, indent=4)
    
    def getStatusFilePath(self):
        return self.__filePath
    
    def getPMID(self):
        return self.__pmid
    
    def getPDFPath(self):
        if not helpers.hasattrdeep(self.__status, ["getPaperPDF", "filename"]):
            raise KeyError("No PDF filename found.")
        
        return os.path.join(ConfigHandler().getPDFsFolderPath(), self.__status['getPaperPDF']['filename'])
    
    def isPDFFetched(self):
        return helpers.hasattrdeep(self.__status, ["getPaperPDF", "success"]) and self.__status["getPaperPDF"]["success"] == True
    
    def isPaperConverted(self):
        return helpers.hasattrdeep(self.__status, ["getPlaintext", "success"]) and self.__status["getPlaintext"]["success"] == True
    
    def getPlaintextFilePath(self):
        if not helpers.hasattrdeep(self.__status, ["getPlaintext", "filename"]):
            raise KeyError("No Plaintext filename found.")
        
        return os.path.join(ConfigHandler().getPlaintextFolderPath(), self.__status['getPlaintext']['filename'])

    def getSummaryFilePath(self):
        if not helpers.hasattrdeep(self.__status, ["getSummary", "filename"]):
            raise KeyError("No Summary filename found.")

        return os.path.join(ConfigHandler().getSummaryFolderPath(), self.__status['getSummary']['filename'])

    def isJSONFetched(self):
        return helpers.hasattrdeep(self.__status, ["getPaperJSON", "success"]) and self.__status["getPaperJSON"]["success"] is True and self.__status["getPaperJSON"]["filename"] == f"{self.__pmid}.json"
    
    def getJSONFilePath(self):
        if not helpers.hasattrdeep(self.__status, ["getPaperJSON", "filename"]):
            raise KeyError("No JSON filename found.")
        
        return os.path.join(ConfigHandler().getJSONFolderPath(), self.__status['getPaperJSON']['filename'])

    def isSummaryFetched(self):
        return helpers.hasattrdeep(self.__status, ["getSummary", "success"]) and self.__status["getSummary"]["success"] == True

    def areSpeciesFetched(self):
        return helpers.hasattrdeep(self.__status, ["getPaperSpecies", "success"]) and self.__status["getPaperSpecies"]["success"] == True
    
    def getSpeciesData(self):
        if not self.areSpeciesFetched():
            raise ValueError("Species are not yet fetched for this paper")
        
        return self.__status["getPaperSpecies"]["response"]
    
    def areGenesFetched(self):
        return helpers.hasattrdeep(self.__status, ["getPaperGenes", "success"]) and self.__status["getPaperGenes"]["success"] == True
    
    def getGenesData(self):
        if not self.areGenesFetched():
            raise ValueError("Genes are not yet fetched for this paper")
        
        return self.__status["getPaperGenes"]
    
    def getGeneSpeciesPairs(self):
        if not self.areGenesFetched():
            raise ValueError("Genes are not yet fetched for this paper")
        
        data = self.__status["getPaperGenes"]["response"]
        pairs = [{"species": s["name"], "geneID": g["identifier"]} for s in data["species"] for g in s["genes"]]
        
        seen = []
        for i, pair in enumerate(pairs):
            if pair in seen:
                pairs.pop(i)
            else:
                seen.append(pair)
        
        return pairs
    
    def areGOTermsFetched(self):
        return helpers.hasattrdeep(self.__status, ["getPaperGOTerms", "success"]) and self.__status["getPaperGOTerms"]["success"] == True
    
    def getFetchedGOTerms(self):
        if not self.areGOTermsFetched():
            raise ValueError("Go terms are not yet fetched for this paper")
        
        return self.__status["getPaperGOTerms"]["goTerms"]
    
    def getGeneSpeciesPairsWithFetchedGOTerms(self):
        if not self.areGOTermsFetched():
            raise ValueError("Go terms are not yet fetched for this paper")
        
        return self.__status["getPaperGOTerms"]["geneSpeciesPairsWithGOTerms"]
    
    def areGOTermDescriptionsValidated(self):
        return helpers.hasattrdeep(self.__status, ["validateGOTermDescriptions", "success"]) and self.__status["validateGOTermDescriptions"]["success"] == True
    
    def getAcceptedGOTerms(self):
        if not self.areGOTermDescriptionsValidated():
            raise ValueError("GO term descriptions have not yet been validated for this paper")
        
        return self.__status["validateGOTermDescriptions"]["acceptedGOTerms"]
    