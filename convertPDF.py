import sys
import os
import json
import config
import utils
from handlers import StatusHandler
from pdfminer.high_level import extract_text

def convertPDF(id):
    statusFilePath = os.path.join(config.getStatusFolderPath(), f"{id}.json")
    
    if not os.path.isfile(statusFilePath):
        raise FileNotFoundError("Status file not found. Download paper to create a status file for it.")
        
    with open(statusFilePath, "r") as statusFile:
        statusData = json.load(statusFile)
        
        if not (utils.hasattrdeep(statusData, ["downloadPaper", "status"]) and statusData["downloadPaper"]["status"] == "downloaded"):
            raise ValueError("Paper with provided ID has not been downloaded")
            
        if utils.hasattrdeep(statusData, ["convertPDF", "status"]) and statusData["convertPDF"]["status"] == "converted":
            raise ValueError("PDF has already been converted to plaintext")
            
        if not utils.hasattrdeep(statusData, ["downloadPaper", "filename"]):
            raise KeyError("File name for this paper not found")
        
    pdfFileName = statusData["downloadPaper"]["filename"]
    pdfFilePath = os.path.join(config.getPDFsFolderPath(), f"{pdfFileName}")
    
    plaintextFilePath = os.path.join(config.getPlaintextFolderPath(), f"{id}.txt")
    if os.path.isfile(plaintextFilePath):
        raise FileExistsError("Plaintext file for this document already exists")
        
    plaintext = extract_text(pdfFilePath)
        
    with open(plaintextFilePath, "w") as plaintextFile:
        plaintextFile.write(plaintext)
            
    statusData["convertPDF"] = {
        "status": "converted",
        "filename": f"{id}.txt"
    }

    with open(statusFilePath, "w") as statusFile:
        json.dump(statusData, statusFile, indent=4)
    

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convertPDF.py <paper_id>")
        sys.exit(1)
        
    id = sys.argv[1]
    
    try:
        convertPDF(id)
    except Exception as err:
        print(f"Error converting PDF to plaintext: {str(err)}")