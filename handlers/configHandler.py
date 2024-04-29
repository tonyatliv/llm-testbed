import json 

class ConfigHandler:
    def __init__(self, file="config.json"):
        self.file = file
        with open(file, "r") as f:
            self.config = json.load(f)
            
    def refresh(self):
        with open(self.file, "r") as f:
            self.config = json.load(f)
            
    def getStatusFolderPath(self):
        return self.config["paths"]["status"]
    
    def getPDFsFolderPath(self):
        return self.config["paths"]["pdf"]
    
    def getPlaintextFolderPath(self):
        return self.config["paths"]["plaintext"]