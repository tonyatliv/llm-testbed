import sys
import os
from handlers import ConfigHandler, StatusHandler
from pdfminer.high_level import extract_text

def convertPDF(id):
    config = ConfigHandler()
    status = StatusHandler(id)
    
    if not status.isPaperDownloaded():
        raise ValueError("Paper with provided ID has not been downloaded")
    
    if status.isPaperConverted():
        raise ValueError("PDF has already been converted to plaintext")

    plaintextFilePath = os.path.join(config.getPlaintextFolderPath(), f"{id}.txt")
    if os.path.isfile(plaintextFilePath):
        raise FileExistsError("Plaintext file for this document already exists")
    
    pdfPath = status.getPDFPath()
    plaintext = extract_text(pdfPath)
        
    with open(plaintextFilePath, "w") as plaintextFile:
        plaintextFile.write(plaintext)
            
    statusData = status.get()
    statusData["convertPDF"] = {
        "status": "converted",
        "filename": f"{id}.txt"
    }
    
    status.update(statusData)
    

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convertPDF.py <paper_id>")
        sys.exit(1)
        
    id = sys.argv[1]
    
    try:
        convertPDF(id)
    except Exception as err:
        print(f"Error converting PDF to plaintext: {str(err)}")