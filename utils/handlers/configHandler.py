import json 
import os
import dotenv

dotenv.load_dotenv()

class ConfigHandler:

    configFile = str(os.getenv("LLM_TESTBED_CONFIG_PATH"))
    
    def __init__(self, file=configFile):
        self.file = file
        configFile = file
        with open(file, "r") as f:
            self.__config = json.load(f)
            
    def getConfig(self):
        return self.__config
            
    def refresh(self):
        with open(self.file, "r") as f:
            self.__config = json.load(f)
            
    def getStatusFolderPath(self):
        return self.__config["paths"]["status"]
    
    def getLLMType(self):
        return self.__config["llm"]["current"]["type"]
    
    def getLLM(self):
        return self.__config["llm"]["current"]["model"]
    
    def getLLMDescription(self):
        return self.__config["llm"]["current"]["description"]

    def getSpecifiedSpecies(self):
        return self.__config["specifiedSpecies"]

    def getPDFsFolderPath(self):
        return self.__config["paths"]["pdf"]
    
    def getPlaintextFolderPath(self):
        return self.__config["paths"]["plaintext"]

    def getSummaryFolderPath(self):
        return self.__config["paths"]["summary"]

    def getJSONFolderPath(self):
        return self.__config["paths"]["sections"]
    
    def getMergeSectionsSections(self):
        return self.__config["getTextFromJSON"]["sections"]

    def getSectionSummarizationPromptForPaperSummary(self):
        return self.__config["getPaperSummary"]["sectionSummarizationPrompt"]

    def getTotalSummarizationPromptForPaperSummary(self):
        return self.__config["getPaperSummary"]["totalSummarizationPrompt"]

    # Get Paper Species
    def getSystemPromptForGetPaperSpecies(self):
        return self.__config["getPaperSpecies"]["systemPrompt"]
    
    def getResponseSchemaForGetPaperSepcies(self):
        return self.__config["getPaperSpecies"]["responseSchema"]
    
    # Get Paper Genes
    def getSystemPromptForGetPaperGenes(self):
        return self.__config["getPaperGenes"]["systemPrompt"]
    
    def getResponseSchemaForGetPaperGenes(self):
        return self.__config["getPaperGenes"]["responseSchema"]
    
    # Get Paper GO Terms
    def getSystemPromptStartForGetPaperGOTerms(self):
        return self.__config["getPaperGOTerms"]["systemPromptStart"]
    
    def getResponseSchemaForGetPaperGOTerms(self):
        return self.__config["getPaperGOTerms"]["responseSchema"]
    
    # Validate GO Term Descriptions
    def getSystemPromptStartForValidateGOTermDescriptions(self):
        return self.__config["validateGOTermDescriptions"]["systemPrompt"]
    
    def getResponseSchemaForValidateGOTermDescriptions(self):
        return self.__config["validateGOTermDescriptions"]["responseSchema"]

    def getResultFolderPath(self):
        return self.__config["paths"]["result"]
    
    def getCacheFolderAPI(self):    
        return self.__config["paths"]["apicache"]
        
